"""GPU detection and configuration utilities."""

import os
import subprocess
from typing import Any

from .logging_config import LoggingMixin


class GPUDetector(LoggingMixin):
    """Handles GPU detection and configuration for OCR processing."""

    def __init__(self) -> None:
        super().__init__()
        self._gpu_available: bool | None = None
        self._gpu_info: str | None = None

    def detect_gpu(self) -> bool:
        """Detect if GPU is available for OCR processing."""
        if self._gpu_available is not None:
            return self._gpu_available

        self.log_info("Starting GPU detection")

        # Check for CUDA availability
        cuda_available = self._check_cuda()

        # Check for OpenCL (fallback)
        opencl_available = self._check_opencl() if not cuda_available else False

        self._gpu_available = cuda_available or opencl_available

        if self._gpu_available:
            self.log_info("GPU acceleration available", gpu_info=self._gpu_info)
        else:
            self.log_info("No GPU acceleration available, using CPU")

        return self._gpu_available

    def _check_cuda(self) -> bool:
        """Check for CUDA availability."""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                self._gpu_info = f"CUDA: {result.stdout.strip()}"
                self.log_debug("CUDA GPU detected", gpu_name=result.stdout.strip())
                return True

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            self.log_debug("CUDA not available or nvidia-smi not found")

        return False

    def _check_opencl(self) -> bool:
        """Check for OpenCL availability."""
        try:
            # Try to import OpenCL libraries
            import pyopencl as cl

            platforms = cl.get_platforms()
            if platforms:
                devices = []
                for platform in platforms:
                    try:
                        devices.extend(platform.get_devices(cl.device_type.GPU))
                    except:
                        continue

                if devices:
                    device_names = [
                        device.name for device in devices[:3]
                    ]  # Limit to 3 devices
                    self._gpu_info = f"OpenCL: {', '.join(device_names)}"
                    self.log_debug("OpenCL GPU detected", devices=device_names)
                    return True

        except ImportError:
            self.log_debug("OpenCL not available - pyopencl not installed")
        except Exception as e:
            self.log_debug("OpenCL detection failed", error=str(e))

        return False

    def configure_for_gpu(self) -> dict[str, Any]:
        """Configure environment variables for GPU usage."""
        # Check for forced CPU usage
        force_cpu = os.getenv("FORCE_CPU", "").lower() in ("true", "1", "yes")

        if force_cpu:
            self.log_info("GPU usage disabled by FORCE_CPU environment variable")
            return {"use_cpu": True, "providers": ["CPUExecutionProvider"]}

        config = {}

        if self.detect_gpu():
            # Set environment variables for GPU usage
            if "CUDA" in (self._gpu_info or ""):
                config.update(
                    {
                        "use_cuda": True,
                        "use_cpu": False,
                        "providers": ["CUDAExecutionProvider", "CPUExecutionProvider"],
                    }
                )
                # Set CUDA environment variables if not already set
                if "CUDA_VISIBLE_DEVICES" not in os.environ:
                    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Use first GPU
                self.log_info("Configured for CUDA GPU acceleration", config=config)
            elif "OpenCL" in (self._gpu_info or ""):
                config.update(
                    {
                        "use_opencl": True,
                        "use_cpu": False,
                        "providers": [
                            "OpenCLExecutionProvider",
                            "CPUExecutionProvider",
                        ],
                    }
                )
                self.log_info("Configured for OpenCL GPU acceleration", config=config)
        else:
            config.update({"use_cpu": True, "providers": ["CPUExecutionProvider"]})
            self.log_info("Configured for CPU processing")

        return config

    def get_gpu_info(self) -> dict[str, Any]:
        """Get GPU information for health checks."""
        self.detect_gpu()  # Ensure detection has run

        return {
            "gpu_available": self._gpu_available or False,
            "gpu_info": self._gpu_info or "Not available",
            "detection_completed": self._gpu_available is not None,
        }


# Global GPU detector instance
gpu_detector = GPUDetector()
