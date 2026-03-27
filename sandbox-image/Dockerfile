FROM python:3.11-slim
WORKDIR /
COPY analyze.py /analyze.py
RUN pip install --no-cache-dir PyPDF2 python-docx pandas
CMD ["python", "/analyze.py"]
