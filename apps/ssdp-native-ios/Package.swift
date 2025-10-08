// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "SSDP",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .library(
            name: "SSDP",
            targets: ["SSDP"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "SSDP",
            dependencies: []
        ),
        .testTarget(
            name: "SSDPTests",
            dependencies: ["SSDP"]
        )
    ]
)
