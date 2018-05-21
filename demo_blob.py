#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from database.mrdatabase import MrDatabase
from database.mrdatabase import LogLevel

""" import of table classes """
from table_schema_examples import Image

database = MrDatabase(os.path.abspath(os.path.join(__file__, os.pardir)), 'test.db')


if __name__ == '__main__':
    # enables logging at 'DEBUG' level
    MrDatabase.logging(level=LogLevel.error)

    # drop tables
    database.drop_table(Image)

    # create tables
    database.create_table(Image)

    for index, image_name in enumerate(os.listdir(os.path.join(os.path.dirname(__file__), 'sample_data'))):

        image_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'sample_data', image_name))

        with open(image_path, 'rb') as image_file:

            image = Image()

            image.id = index
            image.md5 = Image.md5_file_object(image_file)
            image.imageName = image_path
            image.imageData = Image.read_blob_file(image_file)

            database.insert_record(image)

    image2: Image = database.select_record(Image, 'id=2')

    with open(image2.imageName, 'wb') as file:
        file.write(image2.imageData)

    print('done')
