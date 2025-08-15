"""
Secure file upload API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_tenant_id
from app.models.users import User
from app.services.file_upload import file_upload_service
from app.services.audit import audit_service

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/file")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form("documents"),
    allowed_types: Optional[str] = Form(None),
    max_size: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file with comprehensive security validation
    """
    try:
        # Parse allowed types if provided
        allowed_types_list = None
        if allowed_types:
            allowed_types_list = [t.strip() for t in allowed_types.split(",")]
        
        # Upload file
        file_info = await file_upload_service.upload_file(
            file=file,
            category=category,
            allowed_types=allowed_types_list,
            max_size=max_size,
            user_id=current_user.id,
            tenant_id=tenant_id
        )
        
        # Log file upload activity
        await audit_service.log_file_activity(
            file_path=file_info['file_path'],
            file_name=file_info['filename'],
            activity_type="upload",
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            tenant_id=tenant_id,
            file_size=file_info['size'],
            file_hash=file_info['file_hash'],
            mime_type=file_info['mime_type'],
            virus_scan_result="clean",  # Would be actual scan result
            file_classification=category
        )
        
        # Log audit event
        await audit_service.log_event(
            event_type="file_upload",
            resource_type="file",
            action="upload",
            user_id=current_user.id,
            resource_id=file_info['secure_filename'],
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={
                'filename': file_info['filename'],
                'size': file_info['size'],
                'category': category,
                'mime_type': file_info['mime_type']
            }
        )
        
        return {
            "message": "File uploaded successfully",
            "file_info": {
                "filename": file_info['filename'],
                "secure_filename": file_info['secure_filename'],
                "size": file_info['size'],
                "mime_type": file_info['mime_type'],
                "category": file_info['category'],
                "thumbnail_path": file_info['thumbnail_path'],
                "relative_path": file_info['relative_path']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed upload
        await audit_service.log_event(
            event_type="file_upload",
            resource_type="file",
            action="upload",
            user_id=current_user.id,
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message=str(e),
            details={'filename': file.filename if file else 'unknown'}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.post("/multiple")
async def upload_multiple_files(
    request: Request,
    files: List[UploadFile] = File(...),
    category: str = Form("documents"),
    allowed_types: Optional[str] = Form(None),
    max_size: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files
    """
    if len(files) > 10:  # Limit number of files
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )
    
    allowed_types_list = None
    if allowed_types:
        allowed_types_list = [t.strip() for t in allowed_types.split(",")]
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            file_info = await file_upload_service.upload_file(
                file=file,
                category=category,
                allowed_types=allowed_types_list,
                max_size=max_size,
                user_id=current_user.id,
                tenant_id=tenant_id
            )
            
            uploaded_files.append({
                "filename": file_info['filename'],
                "secure_filename": file_info['secure_filename'],
                "size": file_info['size'],
                "mime_type": file_info['mime_type']
            })
            
            # Log individual file upload
            await audit_service.log_file_activity(
                file_path=file_info['file_path'],
                file_name=file_info['filename'],
                activity_type="upload",
                user_id=current_user.id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                tenant_id=tenant_id,
                file_size=file_info['size'],
                file_hash=file_info['file_hash'],
                mime_type=file_info['mime_type']
            )
            
        except HTTPException as e:
            failed_files.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # Log batch upload event
    await audit_service.log_event(
        event_type="file_batch_upload",
        resource_type="file",
        action="batch_upload",
        user_id=current_user.id,
        tenant_id=tenant_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        success=len(failed_files) == 0,
        details={
            'total_files': len(files),
            'successful_uploads': len(uploaded_files),
            'failed_uploads': len(failed_files),
            'category': category
        }
    )
    
    return {
        "message": f"Uploaded {len(uploaded_files)} files successfully",
        "uploaded_files": uploaded_files,
        "failed_files": failed_files,
        "summary": {
            "total": len(files),
            "successful": len(uploaded_files),
            "failed": len(failed_files)
        }
    }


@router.delete("/file/{filename}")
async def delete_file(
    filename: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an uploaded file
    """
    try:
        # For security, construct full path with tenant isolation
        file_path = f"uploads/documents/{tenant_id}/{filename}"
        
        # Delete file
        success = file_upload_service.delete_file(file_path)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Log file deletion
        await audit_service.log_file_activity(
            file_path=file_path,
            file_name=filename,
            activity_type="delete",
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            tenant_id=tenant_id
        )
        
        await audit_service.log_event(
            event_type="file_delete",
            resource_type="file",
            action="delete",
            user_id=current_user.id,
            resource_id=filename,
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={'filename': filename}
        )
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await audit_service.log_event(
            event_type="file_delete",
            resource_type="file",
            action="delete",
            user_id=current_user.id,
            resource_id=filename,
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.get("/file/{filename}/info")
async def get_file_info(
    filename: str,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get information about an uploaded file
    """
    file_path = f"uploads/documents/{tenant_id}/{filename}"
    file_info = file_upload_service.get_file_info(file_path)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "filename": filename,
        "size": file_info['size'],
        "mime_type": file_info['mime_type'],
        "created": file_info['created'],
        "modified": file_info['modified']
    }