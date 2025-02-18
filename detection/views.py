from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import pymysql
import cv2
import numpy as np
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plagiarism_detection.settings')
django.setup()


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')




def home(request):
    return render(request, 'home.html')


def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        return render(request, 'upload.html', {'file_url': file_url})
    return render(request, 'upload.html')


def detect_text_plagiarism(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        text1 = f1.read()
        text2 = f2.read()
    
    words1 = word_tokenize(text1.lower())
    words2 = word_tokenize(text2.lower())
    
    stop_words = set(stopwords.words('english'))
    words1 = [w for w in words1 if w not in stop_words]
    words2 = [w for w in words2 if w not in stop_words]
    
    counter1 = Counter(words1)
    counter2 = Counter(words2)
    
    common_words = set(counter1.keys()) & set(counter2.keys())
    similarity = sum(min(counter1[word], counter2[word]) for word in common_words)
    total_words = sum(counter1.values()) + sum(counter2.values())
    
    return round((2 * similarity / total_words) * 100, 2)


def detect_image_plagiarism(img1, img2):
    image1 = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)
    
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return round(similarity * 100, 2)

def plagiarism_check(request):
    if request.method == 'POST':
        file1 = request.FILES['file1']
        file2 = request.FILES['file2']
        fs = FileSystemStorage()
        file1_path = fs.save(file1.name, file1)
        file2_path = fs.save(file2.name, file2)
        
        if file1.name.endswith('.txt') and file2.name.endswith('.txt'):
            similarity = detect_text_plagiarism(file1_path, file2_path)
        else:
            similarity = detect_image_plagiarism(file1_path, file2_path)
        
        return render(request, 'result.html', {'similarity': similarity})
    return render(request, 'upload.html')