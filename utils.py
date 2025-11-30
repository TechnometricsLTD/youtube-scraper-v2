import os
import requests

def download_image(url, save_dir):
    """
    Downloads an image from the specified URL, renames it to the last part of the URL,
    saves it into the given directory, and returns the full path.
    """
    if not url:
        print("No URL provided.")
        return None

    # Extract filename from URL
    filename = url.rstrip('/').split('/')[-1].split('?')[0]  # Handles URLs with/without query params
    if not filename:
        filename = "downloaded_image"

    # Create the save directory if it does not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, filename)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return save_path
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


# Test code
# if __name__ == "__main__":
#     # Example test image (use any valid image URL)
#     test_url = "https://yt3.ggpht.com/ytc/AIdro_nvLyOxXMFrMZGKIi-LYTnTdleHGUSMZ7-5heal1vo=s88-c-k-c0x00ffffff-no-rj"
#     test_save_dir = "/tmp/youtube/r6BVgEcNXY4"

#     result_path = download_image(test_url, test_save_dir)
#     if result_path and os.path.isfile(result_path):
#         print(f"Image successfully downloaded to: {result_path}")
#     else:
#         print("Image download failed.")


def nest_comments(comment_list, root_id):
    """
    Nest a linear list of Comment objects into a nested structure.
    Each Comment object should have at minimum: comment_id, parent, comments_replies_list.
    :param comment_list: List of Comment dataclass objects, linear.
    :param root_id: The video_id or root comment parent string.
    :return: List of top-level Comment objects, each with replies nested in comments_replies_list.
    """
    # Create a lookup table of all comments by their ID
    # Use the comments directly (they should already have empty comments_replies_list)
    id_to_comment = {c.comment_id: c for c in comment_list}

    nested = []

    for comment in comment_list:
        cid = comment.comment_id
        parent = comment.parent

        # If comment is root level (parent is video_id or parent==root_id)
        if parent == root_id:
            nested.append(id_to_comment[cid])
        else:
            # Find its parent and add to parent's replies list
            if parent in id_to_comment:
                # Append to parent's replies list directly (lists are mutable)
                id_to_comment[parent].comments_replies_list.append(id_to_comment[cid])
            else:
                # Orphaned reply, treat as root-level if parent not found
                nested.append(id_to_comment[cid])

    return nested


