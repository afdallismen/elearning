def attachment_directory(instance, filename):
    return "attachment/{}/{}/{}".format(
        str(instance.content_type.name),
        str(instance.object_id),
        filename
    )
