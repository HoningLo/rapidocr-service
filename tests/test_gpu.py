#!/usr/bin/env python3
"""GPU testing script for RapidOCR service."""

import json
import subprocess
import sys


def test_gpu_access() -> bool:
    """Test GPU access within the container."""
    print("🔍 Testing GPU access...")

    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ NVIDIA GPU detected:")
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    name, memory = line.split(", ")
                    print(f"   - {name}: {memory}")
            return True
        else:
            print("❌ nvidia-smi failed")
            return False
    except Exception as e:
        print(f"❌ GPU access test failed: {e}")
        return False


def test_cuda_availability() -> bool:
    """Test CUDA availability in Python."""
    print("\n🔍 Testing CUDA availability in Python...")

    try:
        import onnxruntime as ort

        available_providers = ort.get_available_providers()
        print(f"📦 Available ONNX providers: {available_providers}")

        if "CUDAExecutionProvider" in available_providers:
            print("✅ CUDA Execution Provider is available")
            return True
        else:
            print("❌ CUDA Execution Provider not available")
            return False

    except ImportError as e:
        print(f"❌ ONNX Runtime import failed: {e}")
        return False


def test_opencl_availability() -> bool:
    """Test OpenCL availability."""
    print("\n🔍 Testing OpenCL availability...")

    try:
        import pyopencl as cl

        platforms = cl.get_platforms()
        print(f"📦 OpenCL platforms found: {len(platforms)}")

        gpu_devices = []
        for platform in platforms:
            try:
                devices = platform.get_devices(device_type=cl.device_type.GPU)
                for device in devices:
                    gpu_devices.append({"name": device.name, "platform": platform.name})
                    print(f"   - {device.name} ({platform.name})")
            except cl.RuntimeError:
                continue

        if gpu_devices:
            print("✅ OpenCL GPU devices available")
            return True
        else:
            print("❌ No OpenCL GPU devices found")
            return False

    except ImportError as e:
        print(f"❌ PyOpenCL import failed: {e}")
        return False


def test_rapidocr_gpu() -> bool:
    """Test RapidOCR with GPU configuration."""
    print("\n🔍 Testing RapidOCR GPU configuration...")

    try:
        from app.gpu_utils import gpu_detector

        # Get GPU info
        gpu_info = gpu_detector.get_gpu_info()
        print("📊 GPU Detection Results:")
        print(json.dumps(gpu_info, indent=2))

        # Configure for GPU
        config = gpu_detector.configure_for_gpu()
        print("🔧 GPU Configuration:")
        print(json.dumps(config, indent=2))

        return gpu_info.get("gpu_available", False)

    except Exception as e:
        print(f"❌ RapidOCR GPU test failed: {e}")
        return False


def main() -> int:
    """Run all GPU tests."""
    print("🚀 Starting GPU Support Tests for RapidOCR Service")
    print("=" * 60)

    tests = [
        ("GPU Access", test_gpu_access),
        ("CUDA Availability", test_cuda_availability),
        ("OpenCL Availability", test_opencl_availability),
        ("RapidOCR GPU", test_rapidocr_gpu),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False

    print(
        f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )

    if all_passed:
        print("🎉 GPU support is properly configured and working!")
    else:
        print(
            "⚠️  Some GPU features may not be available, but CPU fallback should work."
        )

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
