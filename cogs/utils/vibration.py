from PIL import Image
import random
import io

diffs = [(-2, -2), (-2, 2), (2, -2), (2, 2)]


def get_random_value():
    return random.randrange(1, 10) * random.choice([1, -1])


def get_random_image(base_image):
    random_x = get_random_value()
    random_y = get_random_value()
    new_image = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    new_image.paste(base_image, (random_x, random_y))

    return new_image


def get_diff_image(base_image, diff):
    new_image = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    new_image.paste(base_image, diff)

    return new_image


def vibration(image_bytes):
    base_image = Image.open(io.BytesIO(image_bytes))
    all_images = []
    for y in range(1):
        for x in diffs:
            all_images.append(get_diff_image(base_image, x))
            all_images.append(base_image)

    output_buffer = io.BytesIO()
    base_image.save(output_buffer, "gif", save_all=True, append_images=all_images[:-1],
                    loop=0, optimize=False, duratation=20)
    output_buffer.seek(0)

    return output_buffer

