import os
from modules.dbfuncs import MongoDBHandler

root_path = os.path.dirname(os.path.abspath(__file__))
IMAGE_ONE_PATH_RELATIVE = "imgs/test_image1.jpg"
IMAGE_TWO_PATH_RELATIVE = "imgs/test_image2.jpg"
IMAGE_ONE_PATH_ABSOLUTE = root_path + "/imgs/test_image1.jpg"
IMAGE_TWO_PATH_ABSOLUTE = root_path + "/imgs/test_image2.jpg"

if __name__ == "__main__":
    dbfuncs = MongoDBHandler()

    fileCollection = dbfuncs.database["fs.files"]

    image_one_critique = {
        "positive": [
            "The natural light from the window beautifully illuminates the cats, creating a warm and inviting atmosphere.",
            "The contrasting colors of the cats a light cream and a reddish-orange are visually appealing and make them stand out against the background.",
            "The depth of field is shallow, focusing on the cats and blurring the background, which draws attention to the main subjects.",
            "The image tells a simple, charming story of two cats enjoying a sunny afternoon nap.",
            "The inclusion of the child's artwork in the background adds an element of personality and context to the scene.",
        ],
        "negative": [
            "The window screen is slightly distracting, creating a textured pattern that competes with the cats.",
            "The composition could be improved by slightly adjusting the angle to create a more balanced placement of the two cats. Currently, the top cat dominates the space.",
            "The background could be slightly less cluttered.  Some elements outside the window and the child's drawing feel somewhat distracting.",
            "The hanging cat bed appears slightly out of alignment, which detracts from the overall neatness of the image.",
        ],
        "overview": "The photograph is a charming and heartwarming depiction of two cats napping. The use of natural light and the warm tones are very effective.  However, some minor adjustments to the composition, such as a slightly different angle and potentially less cluttered background, could further enhance the image's overall impact. The juxtaposition of the domestic scene with the child's artwork adds an interesting layer of context.",
    }

    image_two_critique = {
        "positive": [
            "The cat is the clear focal point, and its cute face and name tag are well-presented.",
            "The color contrast between the white cat, the orange, and the red apples is visually appealing.",
            "The depth of field is shallow, focusing on the cats and blurring the background, which draws attention to the main subjects.",
            "The shallow depth of field blurs the background, drawing attention to the cat and the fruit.",
            "The slightly unusual angle adds a bit of intrigue.",
        ],
        "negative": [
            "The background is cluttered and distracting.  The various objects (cleaning supplies, newspaper) compete for attention and detract from the main subject.",
            "The lighting is uneven. The cat is well-lit, but some parts of the background are darker and less defined.",
            "The two-tiered serving tray feels somewhat awkward and doesn't enhance the overall composition. It could be considered unnecessary.",
            "The story is unclear.  While the image is visually pleasant, it lacks a narrative or compelling message. What's the connection between the cat, the fruit, and the background elements?",
        ],
        "overview": "The photo is technically competent in terms of focus and color, but the composition suffers from a cluttered background and lack of a clear narrative.  While the cat is undeniably cute and the colors work well together, the overall effect is somewhat muddled.  A simpler background and better lighting would significantly improve the image's impact. A tighter crop, focusing more closely on the cat and the fruit, might improve the overall impression.",
    }

    image_one_id = dbfuncs.add_image(IMAGE_ONE_PATH_ABSOLUTE)
    dbfuncs.add_critique(image_one_id, image_one_critique)
    image_two_id = dbfuncs.add_image(IMAGE_TWO_PATH_ABSOLUTE)
    dbfuncs.add_critique(image_two_id, image_two_critique)

    theme_one_name = "Motion_Blur_Effects"
    description = "Photograph a subject in motion, like a fast-moving vehicle or a person running, with a slow shutter speed to create a sense of blur and dynamism."
    dbfuncs.add_theme(theme_one_name, description)

    print("\nDone Seeding Database")
