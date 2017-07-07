from django.shortcuts import render
from django.http import  HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from . import utils as image_utils
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import json
import datetime
import urllib
import os.path
import jwt

permissions = {AllowAny, }


class Index(APIView):
    template_name = 'simple_upload.html'

    def get(self, request):
        return render(request, self.template_name)

    """
    function used for post endpoint which uploads the image 
    takes the image to be uploaded in the post data  
    first it checks the token which is sent in the header 
    if it is correct then it gets the image from the post data and extracts its extension
    if the extension is not that of an image then it returns an error
    if the extension is correct it open the FileSystemStorage and appends the access token 
    with the image name and saves the image     
    else it throws the suitable error 
    """


    def post(self, request):
        error = ''
        uploaded_image_url = ''
        uploaded_image = ''
        jwtToken = request.META['HTTP_AUTHORIZATION']
        try:
            fs = FileSystemStorage()
            payload = jwt.decode(jwtToken, 'bhandari', True)
            if not request.FILES.get('image_file') and not request.POST.get('image_url'):
                return HttpResponse(json.dumps({"image_url": '', "error": "Send either imahge or url"}))
            if request.FILES.get('image_file'):
                image_file = request.FILES['image_file']
                extension = os.path.splitext(image_file.name)[1]
                if not (extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                    return HttpResponse(json.dumps({"image_url": '', "error": 'Unsupportable type'}))
                image_path = settings.MEDIA_ROOT + '/'
                # appending access token to track which image belongs to which token
                # appending timestamp so that if image with same name is posted previous is not deleted
                image_name = jwtToken + "_"+str(datetime.datetime.now())+"_"+image_file.name
                fs.save(image_name, image_file)
                # compression of image to decrease the size
                compress_response = image_utils.compress_image(image_path, image_name)
                if not compress_response.get('status'):
                    error = compress_response.get('error')
                else:
                    uploaded_image = compress_response.get('compressed_image_path')
                    fs.delete(image_name)
            if request.POST.get('image_url'):
                image_url = request.POST.get('image_url')
                image_name = image_url.rsplit('/', 1)[1]
                extension = os.path.splitext(image_name)[1]
                if not (extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                    return HttpResponse(json.dumps({"image_url": '', "error": "Unsupportable type"}))
                image_path = settings.MEDIA_ROOT + '/'
                uploaded_image_url = jwtToken + "_"+str(datetime.datetime.now())+"_"+image_name
                urllib.urlretrieve(image_url, image_path + uploaded_image_url )
                # compression of image to decrease the size
                compress_response = image_utils.compress_image(image_path, uploaded_image_url)
                if not compress_response.get('status'):
                    error = compress_response.get('error')
                else:
                    fs.delete(uploaded_image_url)
                    uploaded_image_url = compress_response.get('compressed_image_path')


        except jwt.ExpiredSignature:
            error = "Signature Expired"
        except jwt.DecodeError:
            error = "Decoding Error"
        except jwt.InvalidTokenError:
            error = "Invalid Token"
        except Exception:
            error = "Image not found at the given URL"



        return HttpResponse(json.dumps({"image": uploaded_image,"image_url" : uploaded_image_url,"error":error}))

"""
function used for get endpoint for both single image and all the images 
takes the image_name in the arguments if it is not given then it will return
all the images linked to the given access token 
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name and linked to the access token exits 
if it does then it returns the image path
if image_name is null this implies that getImages/ endpoint was used 
so it returns all the images 
else it throws the suitable error 

:param image_name:
"""
def get_images(request, image_name=""):

    jwtToken = request.META['HTTP_AUTHORIZATION']
    images = []
    image = []
    error = "False"
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        if image_name:
            fs = FileSystemStorage()
            files = fs.listdir('')
            if not files[1]:
                return HttpResponse(json.dumps({"image": image, "images": images, "error": "no images in media folder"}))
            # for f in files:
            for img in files[1]:
                if jwtToken in img and image_name in img:
                    image.append("/media/" + img)
            if not image:
                error = "no image by the given name or given token"

        else:
            fs = FileSystemStorage()
            files = fs.listdir('')
            if not files[1]:
                return HttpResponse(
                    json.dumps({"image": image, "images": images, "error": "no images in media folder"}))
            # for f in files:
            for img in files[1]:
                if jwtToken in img:
                    images.append("/media/" + img)
            if not images:
                error = "no images for given token"
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.InvalidTokenError:
        error = "Invalid Token"
    return HttpResponse(json.dumps({"image": image, "images": images, "error": error}))

"""
function used for delete endpoint 
takes the image to be deleted in the url 
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name exits 
if it does then it deletes the image 
else it throws the suitable error 
:param image_name:
"""
def delete(request, image_name):
    error = "False"
    msg = ""
    flag=1
    jwtToken = request.META['HTTP_AUTHORIZATION']
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        fs = FileSystemStorage()
        files = fs.listdir('')
        if not files[1]:
            return HttpResponse(json.dumps({"msg":"", "error": "no images in media folder"}))

        for img in files[1]:
            if jwtToken in img and image_name in img:
                fs.delete(img)
                msg = "image deleted"
                flag = 0
        if flag == 1:
            error = "no images by the given name or given token"
    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.InvalidTokenError:
        error = "Invalid Token"
    return HttpResponse(json.dumps({"msg": msg, "error": error}))

"""
function used for patch endpoint 
takes the image to be updated in the url and the image file in the post data
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name exits 
if it does then it deletes the image 
and replaces it with the new image that is sent in the post data
else it throws the suitable error
:param image_name:
"""
@csrf_exempt
def patch(request, image_name_delete):
    error = "False"
    uploaded_file_url = ""
    flag = 1
    jwtToken = request.META['HTTP_AUTHORIZATION']
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        if not request.FILES.get('image_file') and not request.POST.get('image_url'):
            return HttpResponse(json.dumps({"image_url": '', "error": "no image sent to be patched"}))
        if request.method == 'POST' and request.FILES['image_file']:
            fs = FileSystemStorage()
            files = fs.listdir('')
            if not files[1]:
                return HttpResponse(
                    json.dumps({"image_url": "", "error": "no images in media folder"}))

            for img in files[1]:
                if jwtToken in img and image_name_delete in img:
                    fs.delete(img)
                    flag = 0
            if flag == 1:
                error = "no image found by the given name or given token"
                return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))
            image_file = request.FILES['image_file']
            extension = os.path.splitext(image_file.name)[1]
            if not (extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": "Unsupportable type"}))
            fs = FileSystemStorage()
            image_name_patch = jwtToken + "_" + str(datetime.datetime.now()) + "_" + image_file.name
            fs.save(image_name_patch, image_file)
            image_path = settings.MEDIA_ROOT + '/'
            compress_response = image_utils.compress_image(image_path, image_name_patch)
            if not compress_response.get('status'):
                error = compress_response.get('error')
            else:
                fs.delete(image_name_patch)
                uploaded_file_url = compress_response.get('compressed_image_path')

                return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))

    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.InvalidTokenError:
        error = "Invalid Token"

    return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))

"""
 function used to generate the access token
 randomly generates a string of length 5 which is used to generate the token
 bhandari is the secret key
 the generated token has to be attached in the header with every request
"""
def generate_token(request):
    data = {
        'username': get_random_string(length=5)
    }

    payload = jwt.encode(data, 'bhandari', 'HS256')

    return HttpResponse(json.dumps({"payload": payload}))
