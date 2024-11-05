import pytest

from inference.core.entities.requests.owlv2 import OwlV2InferenceRequest
from inference.models.owlv2.owlv2 import OwlV2


@pytest.mark.slow
def test_owlv2():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test we can handle a single positive prompt
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 223,
                        "y": 306,
                        "w": 40,
                        "h": 226,
                        "cls": "post",
                        "negative": False,
                    },
                ],
            }
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    # we assert that we're finding all of the posts in the image
    assert len(response.predictions) == 5
    # next we check the x coordinates to force something about localization
    # the exact value here is sensitive to:
    # 1. the image interpolation mode used
    # 2. the data type used in the model, ie bfloat16 vs float16 vs float32
    # 3. the size of the model itself, ie base vs large
    # 4. the specific hardware used to run the model
    # we set a tolerance of 1.5 pixels from the expected value, which should cover most of the cases
    # first we sort by x coordinate to make sure we're getting the correct post
    posts = [p for p in response.predictions if p.class_name == "post"]
    posts.sort(key=lambda x: x.x)
    assert abs(223 - posts[0].x) < 1.5
    assert abs(248 - posts[1].x) < 1.5
    assert abs(264 - posts[2].x) < 1.5
    assert abs(532 - posts[3].x) < 1.5
    assert abs(572 - posts[4].x) < 1.5


@pytest.mark.slow
def test_owlv2_multiple_prompts():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test we can handle multiple (positive and negative) prompts for the same image
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 223,
                        "y": 306,
                        "w": 40,
                        "h": 226,
                        "cls": "post",
                        "negative": False,
                    },
                    {
                        "x": 247,
                        "y": 294,
                        "w": 25,
                        "h": 165,
                        "cls": "post",
                        "negative": True,
                    },
                    {
                        "x": 264,
                        "y": 327,
                        "w": 21,
                        "h": 74,
                        "cls": "post",
                        "negative": False,
                    },
                ],
            }
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 4
    posts = [p for p in response.predictions if p.class_name == "post"]
    posts.sort(key=lambda x: x.x)
    assert abs(223 - posts[0].x) < 1.5
    assert abs(264 - posts[1].x) < 1.5
    assert abs(532 - posts[2].x) < 1.5
    assert abs(572 - posts[3].x) < 1.5


@pytest.mark.slow
def test_owlv2_image_without_prompts():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test that we can handle an image without any prompts
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 223,
                        "y": 306,
                        "w": 40,
                        "h": 226,
                        "cls": "post",
                        "negative": False,
                    }
                ],
            },
            {
                "image": image,
                "boxes": [],
            },
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 5


@pytest.mark.slow
def test_owlv2_bad_prompt():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test that we can handle a bad prompt
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 1,
                        "y": 1,
                        "w": 1,
                        "h": 1,
                        "cls": "post",
                        "negative": False,
                    }
                ],
            }
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 0


@pytest.mark.slow
def test_owlv2_bad_prompt_hidden_among_good_prompts():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test that we can handle a bad prompt
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 1,
                        "y": 1,
                        "w": 1,
                        "h": 1,
                        "cls": "post",
                        "negative": False,
                    },
                    {
                        "x": 223,
                        "y": 306,
                        "w": 40,
                        "h": 226,
                        "cls": "post",
                        "negative": False,
                    },
                ],
            }
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 5


@pytest.mark.slow
def test_owlv2_no_training_data():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }

    # test that we can handle no training data
    request = OwlV2InferenceRequest(
        image=image,
        training_data=[],
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 0


@pytest.mark.slow
def test_owlv2_multiple_training_images():
    image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/seawithdock.jpeg",
    }
    second_image = {
        "type": "url",
        "value": "https://media.roboflow.com/inference/dock2.jpg",
    }

    request = OwlV2InferenceRequest(
        image=image,
        training_data=[
            {
                "image": image,
                "boxes": [
                    {
                        "x": 223,
                        "y": 306,
                        "w": 40,
                        "h": 226,
                        "cls": "post",
                        "negative": False,
                    }
                ],
            },
            {
                "image": second_image,
                "boxes": [
                    {
                        "x": 3009,
                        "y": 1873,
                        "w": 289,
                        "h": 811,
                        "cls": "post",
                        "negative": True,
                    }
                ],
            },
        ],
        visualize_predictions=True,
        confidence=0.9,
    )

    response = OwlV2().infer_from_request(request)
    assert len(response.predictions) == 5


if __name__ == "__main__":
    test_owlv2()
