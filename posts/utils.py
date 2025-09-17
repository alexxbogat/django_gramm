from posts.models import Tag, Post


def parse_and_add_tags(tag_string: str, post: Post) -> None:
    """Parses a comma-separated string of tags and associates them with a post.

    Args:
        tag_string: A string of tag names separated by commas.
        post: The Post object to associate the tags with.
    """
    tag_names = [name.strip().lower() for name in tag_string.split(',') if name.strip()]
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name)
        post.tags.add(tag)
