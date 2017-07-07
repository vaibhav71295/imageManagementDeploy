from PIL import Image


def compress_image(image_path,image_name):
    """
    Function to compress the image to 50% of its quality
    :param image_path:
    :param image_name:
    :return:
    """
    try:
        quality = 50
        compress_params = {"quality": quality, "optimised": True}
        if image_name.split('.')[1] == 'gif':
            compress_params = {"quality": quality, "optimised": True, 'save_all': True}
        image = Image.open(image_path + image_name)
        image.save(image_path + 'compressed_'+str(quality) + image_name,**compress_params)
        response = {'error': '', 'status': True, 'compressed_image_path': '/media/' + 'compressed_'+str(quality) +image_name}
    except IOError:
        response = {'error': 'Problem in saving the file', 'status': False, 'compressed_image_path': ''}

    return response


