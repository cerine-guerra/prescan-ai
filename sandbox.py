import docker
import tempfile
import os

def run_sandbox(file_bytes: bytes, filename: str) -> str:
    client = docker.from_env()
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        try:
            output = client.containers.run(
                image="prescan-sandbox",
                command=f"python /analyze.py /sample/{filename}",
                volumes={tmpdir: {"bind": "/sample", "mode": "ro"}},
                network_disabled=True,
                mem_limit="128m",
                remove=True,
                stdout=True,
                stderr=False,
                timeout=30
            )
            return output.decode("utf-8")
        except docker.errors.ContainerError as e:
            return f"CONTAINER_ERROR: {str(e)}"
        except Exception as e:
            return f"SANDBOX_ERROR: {str(e)}"
