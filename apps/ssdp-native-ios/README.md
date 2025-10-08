# SSDP Native iOS App

Native iOS application built with SwiftUI for SSDP platform.

## Features

- Native iOS performance
- SwiftUI modern UI framework
- Arabic/English bilingual support with RTL
- Biometric authentication (Face ID/Touch ID)
- Offline-first with Core Data
- Push notifications via APNs
- App Store Connect integration

## Requirements

- Xcode 15.0+
- iOS 16.0+
- Swift 5.9+

## Setup

```bash
# Open in Xcode
open SSDP.xcodeproj

# Or build from command line
xcodebuild -scheme SSDP -configuration Debug
```

## Architecture

- **SwiftUI**: Modern declarative UI
- **Combine**: Reactive programming
- **Core Data**: Local persistence
- **Swift Concurrency**: async/await
- **MVVM**: Architecture pattern

## Testing

```bash
# Run unit tests
xcodebuild test -scheme SSDP -destination 'platform=iOS Simulator,name=iPhone 15'

# Run UI tests
xcodebuild test -scheme SSDPUITests -destination 'platform=iOS Simulator,name=iPhone 15'
```

## Build & Distribution

```bash
# Archive for distribution
xcodebuild archive -scheme SSDP -archivePath ./build/SSDP.xcarchive

# Export for App Store
xcodebuild -exportArchive -archivePath ./build/SSDP.xcarchive -exportPath ./build/SSDP -exportOptionsPlist ExportOptions.plist
```

## App Store

- Team ID: WMQ3ZFI6RQAM
- Bundle ID: com.brainsait.ssdp
- Apple Pay Merchant ID: merchant.io.brainsait.ssdp
