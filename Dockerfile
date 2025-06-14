# Use the official Python image from Microsoft Codespaces
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install required Python packages globally
RUN pip install moviepy Pillow requests