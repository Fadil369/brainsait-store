"""
Field Sales service for business logic
"""

import base64
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID
import io

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.field_sales import (
    SalesRep,
    OutletCheckIn,
    VoiceOrder,
    CreditRequest,
    Leaderboard,
    Achievement,
    SalesRepStatus,
    CheckInStatus,
    CreditStatus,
)


class FieldSalesService:
    """Service for field sales operations"""

    def __init__(self, db: Session):
        self.db = db

    # Sales Rep Operations
    def get_sales_rep(self, rep_id: UUID) -> Optional[SalesRep]:
        """Get sales rep by ID"""
        return self.db.query(SalesRep).filter(SalesRep.id == rep_id).first()

    def get_sales_rep_by_code(self, rep_code: str, tenant_id: str) -> Optional[SalesRep]:
        """Get sales rep by code"""
        return (
            self.db.query(SalesRep)
            .filter(
                SalesRep.rep_code == rep_code,
                SalesRep.tenant_id == tenant_id,
            )
            .first()
        )

    def get_sales_rep_by_user_id(self, user_id: UUID, tenant_id: str) -> Optional[SalesRep]:
        """Get sales rep by user ID"""
        return (
            self.db.query(SalesRep)
            .filter(
                SalesRep.user_id == user_id,
                SalesRep.tenant_id == tenant_id,
            )
            .first()
        )

    def create_sales_rep(self, rep_data: Dict[str, Any], tenant_id: str) -> SalesRep:
        """Create a new sales rep"""
        sales_rep = SalesRep(
            tenant_id=tenant_id,
            **rep_data,
        )
        self.db.add(sales_rep)
        self.db.commit()
        self.db.refresh(sales_rep)
        return sales_rep

    def update_sales_rep(self, rep_id: UUID, update_data: Dict[str, Any]) -> Optional[SalesRep]:
        """Update sales rep"""
        sales_rep = self.get_sales_rep(rep_id)
        if not sales_rep:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(sales_rep, key):
                setattr(sales_rep, key, value)

        self.db.commit()
        self.db.refresh(sales_rep)
        return sales_rep

    # Check-in Operations
    def create_check_in(
        self, sales_rep_id: UUID, check_in_data: Dict[str, Any], tenant_id: str
    ) -> OutletCheckIn:
        """Create outlet check-in"""
        # Verify geofence if outlet_id provided
        geofence_verified = False
        distance = None
        
        if check_in_data.get("outlet_id"):
            # TODO: Implement actual geofence verification
            # This would check if the lat/long is within acceptable range of outlet
            geofence_verified = True
            distance = 0.0  # Placeholder

        # Handle photo upload
        photo_url = None
        if check_in_data.get("photo_base64"):
            photo_url = self._save_photo(check_in_data["photo_base64"], sales_rep_id)

        check_in = OutletCheckIn(
            sales_rep_id=sales_rep_id,
            tenant_id=tenant_id,
            outlet_name=check_in_data["outlet_name"],
            outlet_id=check_in_data.get("outlet_id"),
            latitude=check_in_data["latitude"],
            longitude=check_in_data["longitude"],
            address=check_in_data.get("address"),
            geofence_verified=geofence_verified,
            distance_from_outlet=distance,
            photo_url=photo_url,
            visit_notes=check_in_data.get("visit_notes"),
            products_discussed=check_in_data.get("products_discussed"),
        )

        self.db.add(check_in)
        
        # Update sales rep stats
        sales_rep = self.get_sales_rep(sales_rep_id)
        if sales_rep:
            sales_rep.total_visits += 1
            sales_rep.last_active_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(check_in)
        return check_in

    def update_check_in(self, check_in_id: UUID, update_data: Dict[str, Any]) -> Optional[OutletCheckIn]:
        """Update check-in (e.g., check-out)"""
        check_in = self.db.query(OutletCheckIn).filter(OutletCheckIn.id == check_in_id).first()
        if not check_in:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(check_in, key):
                setattr(check_in, key, value)

        # Calculate duration if checking out
        if update_data.get("check_out_time"):
            duration = (update_data["check_out_time"] - check_in.check_in_time).total_seconds() / 60
            check_in.duration_minutes = int(duration)

        self.db.commit()
        self.db.refresh(check_in)
        return check_in

    def get_rep_check_ins(
        self,
        sales_rep_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[OutletCheckIn]:
        """Get check-ins for a sales rep"""
        query = self.db.query(OutletCheckIn).filter(OutletCheckIn.sales_rep_id == sales_rep_id)

        if start_date:
            query = query.filter(OutletCheckIn.check_in_time >= start_date)
        if end_date:
            query = query.filter(OutletCheckIn.check_in_time <= end_date)

        return query.order_by(OutletCheckIn.check_in_time.desc()).limit(limit).all()

    # Voice Order Operations
    def create_voice_order(
        self, sales_rep_id: UUID, voice_data: Dict[str, Any], tenant_id: str
    ) -> VoiceOrder:
        """Create voice order (stub for speech recognition integration)"""
        # Save audio file
        audio_url = None
        if voice_data.get("audio_base64"):
            audio_url = self._save_audio(voice_data["audio_base64"], sales_rep_id)

        voice_order = VoiceOrder(
            sales_rep_id=sales_rep_id,
            tenant_id=tenant_id,
            audio_url=audio_url,
            audio_duration_seconds=voice_data.get("audio_duration_seconds"),
            language=voice_data.get("language", "ar"),
            processing_status="pending",
        )

        self.db.add(voice_order)
        self.db.commit()
        self.db.refresh(voice_order)

        # TODO: Queue for async processing with speech recognition service
        # This would integrate with services like Google Speech-to-Text, Azure Speech, etc.

        return voice_order

    def process_voice_order(self, voice_order_id: UUID, transcription: str) -> VoiceOrder:
        """Process voice order transcription"""
        voice_order = self.db.query(VoiceOrder).filter(VoiceOrder.id == voice_order_id).first()
        if not voice_order:
            return None

        voice_order.raw_transcription = transcription
        voice_order.processed_text = transcription
        voice_order.processing_status = "completed"
        voice_order.processed_at = datetime.utcnow()

        # TODO: Extract products and customer info from transcription
        # This would use NLP to parse the order details

        self.db.commit()
        self.db.refresh(voice_order)
        return voice_order

    # Credit Request Operations
    def create_credit_request(
        self, sales_rep_id: UUID, credit_data: Dict[str, Any], tenant_id: str
    ) -> CreditRequest:
        """Create credit request with AI assessment"""
        credit_request = CreditRequest(
            sales_rep_id=sales_rep_id,
            tenant_id=tenant_id,
            customer_name=credit_data["customer_name"],
            customer_email=credit_data.get("customer_email"),
            customer_phone=credit_data["customer_phone"],
            customer_business=credit_data.get("customer_business"),
            requested_amount=credit_data["requested_amount"],
            credit_term_days=credit_data.get("credit_term_days", 30),
            purpose=credit_data.get("purpose"),
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        # AI Assessment (stub for ML model integration)
        ai_score, ai_recommendation, risk_factors = self._assess_credit_risk(credit_data)
        credit_request.ai_score = ai_score
        credit_request.ai_recommendation = ai_recommendation
        credit_request.risk_factors = risk_factors

        self.db.add(credit_request)
        self.db.commit()
        self.db.refresh(credit_request)
        return credit_request

    def update_credit_request(
        self, credit_id: UUID, update_data: Dict[str, Any], decided_by: Optional[UUID] = None
    ) -> Optional[CreditRequest]:
        """Update credit request decision"""
        credit_request = self.db.query(CreditRequest).filter(CreditRequest.id == credit_id).first()
        if not credit_request:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(credit_request, key):
                setattr(credit_request, key, value)

        if decided_by:
            credit_request.decided_by = decided_by
            credit_request.decided_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(credit_request)
        return credit_request

    def get_rep_credit_requests(
        self, sales_rep_id: UUID, status: Optional[str] = None, limit: int = 50
    ) -> List[CreditRequest]:
        """Get credit requests for a sales rep"""
        query = self.db.query(CreditRequest).filter(CreditRequest.sales_rep_id == sales_rep_id)

        if status:
            query = query.filter(CreditRequest.status == status)

        return query.order_by(CreditRequest.created_at.desc()).limit(limit).all()

    # Dashboard & Analytics
    def get_dashboard_data(self, sales_rep_id: UUID) -> Dict[str, Any]:
        """Get comprehensive dashboard data for sales rep"""
        sales_rep = self.get_sales_rep(sales_rep_id)
        if not sales_rep:
            return None

        # Target progress
        target_progress = self._calculate_target_progress(sales_rep)

        # Recent check-ins
        recent_check_ins = self.get_rep_check_ins(sales_rep_id, limit=10)

        # Pending credits
        pending_credits = self.get_rep_credit_requests(sales_rep_id, status="pending", limit=10)

        # Leaderboard position
        leaderboard_position = self._get_leaderboard_position(sales_rep_id, sales_rep.tenant_id)

        # Achievements
        achievements = self._get_rep_achievements(sales_rep_id, sales_rep.tenant_id)

        # Route summary (today's visits)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_check_ins = self.get_rep_check_ins(sales_rep_id, start_date=today_start)

        return {
            "rep_info": sales_rep,
            "target_progress": target_progress,
            "recent_check_ins": recent_check_ins,
            "pending_credits": pending_credits,
            "leaderboard_position": leaderboard_position,
            "achievements": achievements,
            "route_summary": {
                "total_visits_today": len(today_check_ins),
                "completed_visits": len([c for c in today_check_ins if c.check_out_time]),
                "in_progress": len([c for c in today_check_ins if not c.check_out_time]),
            },
        }

    # Gamification
    def update_gamification(self, sales_rep_id: UUID, action: str, value: Any = None) -> None:
        """Update gamification points and achievements"""
        sales_rep = self.get_sales_rep(sales_rep_id)
        if not sales_rep:
            return

        # Award points based on action
        points_map = {
            "check_in": 10,
            "check_out": 15,
            "order_created": 50,
            "credit_approved": 100,
            "target_achieved": 500,
        }

        points = points_map.get(action, 0)
        sales_rep.points += points

        # Check for level up (every 1000 points = 1 level)
        new_level = sales_rep.points // 1000 + 1
        if new_level > sales_rep.level:
            sales_rep.level = new_level

        # Check for achievements
        self._check_achievements(sales_rep)

        self.db.commit()

    def get_leaderboard(
        self, tenant_id: str, period_type: str = "monthly", limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for a period"""
        # Calculate period dates
        now = datetime.utcnow()
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "weekly":
            period_start = now - timedelta(days=now.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
        else:  # monthly
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = now.replace(year=now.year + 1, month=1, day=1)
            else:
                period_end = now.replace(month=now.month + 1, day=1)

        # Query leaderboard
        leaderboard = (
            self.db.query(Leaderboard)
            .filter(
                Leaderboard.tenant_id == tenant_id,
                Leaderboard.period_type == period_type,
                Leaderboard.period_start == period_start,
            )
            .order_by(Leaderboard.rank)
            .limit(limit)
            .all()
        )

        return leaderboard

    # Helper Methods
    def _save_photo(self, base64_data: str, sales_rep_id: UUID) -> str:
        """Save base64 photo and return URL (stub)"""
        # TODO: Implement actual file storage (S3, Cloudflare R2, etc.)
        filename = f"checkin_{sales_rep_id}_{datetime.utcnow().timestamp()}.jpg"
        return f"/uploads/photos/{filename}"

    def _save_audio(self, base64_data: str, sales_rep_id: UUID) -> str:
        """Save base64 audio and return URL (stub)"""
        # TODO: Implement actual file storage
        filename = f"voice_{sales_rep_id}_{datetime.utcnow().timestamp()}.mp3"
        return f"/uploads/audio/{filename}"

    def _assess_credit_risk(self, credit_data: Dict[str, Any]) -> tuple:
        """AI-based credit risk assessment (stub)"""
        # TODO: Integrate with ML model for actual risk assessment
        # This is a placeholder that returns mock data
        
        # Simple rule-based scoring for demo
        score = 75.0  # Default medium risk
        amount = float(credit_data.get("requested_amount", 0))
        
        if amount < 10000:
            score = 85.0
        elif amount > 50000:
            score = 60.0
        
        recommendation = "approve" if score >= 70 else "review" if score >= 50 else "reject"
        
        risk_factors = []
        if amount > 50000:
            risk_factors.append("High credit amount")
        if credit_data.get("credit_term_days", 30) > 90:
            risk_factors.append("Extended credit term")
        
        return score, recommendation, risk_factors

    def _calculate_target_progress(self, sales_rep: SalesRep) -> Dict[str, Any]:
        """Calculate target achievement progress"""
        now = datetime.utcnow()
        days_in_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        days_remaining = (days_in_month - now).days + 1

        progress_percentage = (
            float(sales_rep.current_month_sales / sales_rep.monthly_target * 100)
            if sales_rep.monthly_target > 0
            else 0
        )

        remaining_amount = sales_rep.monthly_target - sales_rep.current_month_sales
        daily_average_required = remaining_amount / days_remaining if days_remaining > 0 else 0

        return {
            "monthly_target": sales_rep.monthly_target,
            "current_sales": sales_rep.current_month_sales,
            "progress_percentage": round(progress_percentage, 2),
            "days_remaining": days_remaining,
            "daily_average_required": daily_average_required,
        }

    def _get_leaderboard_position(self, sales_rep_id: UUID, tenant_id: str) -> Dict[str, Any]:
        """Get current leaderboard position"""
        # TODO: Implement actual leaderboard calculation
        return {
            "rank": 1,
            "total_participants": 1,
            "percentile": 100,
        }

    def _get_rep_achievements(self, sales_rep_id: UUID, tenant_id: str) -> List[Dict[str, Any]]:
        """Get achievements for sales rep"""
        sales_rep = self.get_sales_rep(sales_rep_id)
        if not sales_rep or not sales_rep.badges:
            return []

        # Get all available achievements
        achievements = self.db.query(Achievement).filter(
            Achievement.tenant_id == tenant_id, Achievement.is_active == True
        ).all()

        earned_badges = sales_rep.badges or []
        
        return [
            {
                "id": str(achievement.id),
                "code": achievement.code,
                "name": achievement.name,
                "name_ar": achievement.name_ar,
                "badge_type": achievement.badge_type,
                "is_earned": achievement.code in earned_badges,
            }
            for achievement in achievements
        ]

    def _check_achievements(self, sales_rep: SalesRep) -> None:
        """Check and award achievements"""
        # Get all available achievements
        achievements = self.db.query(Achievement).filter(
            Achievement.tenant_id == sales_rep.tenant_id,
            Achievement.is_active == True,
        ).all()

        earned_badges = sales_rep.badges or []

        for achievement in achievements:
            if achievement.code in earned_badges:
                continue

            # Check if achievement is earned
            earned = False
            if achievement.requirement_type == "sales":
                earned = sales_rep.total_sales >= achievement.requirement_value
            elif achievement.requirement_type == "visits":
                earned = sales_rep.total_visits >= achievement.requirement_value
            elif achievement.requirement_type == "points":
                earned = sales_rep.points >= achievement.requirement_value

            if earned:
                earned_badges.append(achievement.code)
                sales_rep.points += achievement.points_reward

        sales_rep.badges = earned_badges
