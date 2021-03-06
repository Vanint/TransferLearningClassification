from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.append('../')
import tensorflow as tf
import glob
import numpy as np
import matplotlib.pyplot as plt
from database import dataset_reader


def estimated_mean(mode='train', dataset='dogs120', resize_image_size=256):
    with tf.device('/cpu:0'):
        image_size = resize_image_size

        feature_map = {
            'image/encoded': tf.FixedLenFeature([], dtype=tf.string,
                                                default_value=''),
            'image/class/trainid': tf.FixedLenFeature([1], dtype=tf.int64,
                                                      default_value=-1),
            'image/filename': tf.FixedLenFeature([], dtype=tf.string,
                                                default_value='')
        }

        if dataset == 'indoors67':
            data_path = '../create_databases/tfRecords-Indoors/Train-*'
            if 'val' in mode or 'test' in mode:
                data_path = '../create_databases/tfRecords-Indoors/Test-*'
        elif dataset == 'dogs120':
            data_path = '../create_databases/tfRecords-Dogs/train-*'
            if 'val' in mode or 'test' in mode:
                data_path = '../create_databases/tfRecords-Dogs/test-*'
        elif dataset == 'foods101':
            data_path = '../create_databases/tfRecords-Foods/train-*'
            if 'val' in mode or 'test' in mode:
                data_path = '../create_databases/tfRecords-Foods/test-*'
        elif dataset == 'caltech256':
            data_path = '../create_databases/tfRecords-Caltech/train*'
            if 'test' in mode:
                data_path = '../create_databases/tfRecords-Caltech/test-*'
            if 'rest' in mode:
                data_path = '../create_databases/tfRecords-Caltech/rest-*'
        elif dataset == 'places365':
            data_path = '../create_databases/tfRecords-Places/train*'
            if 'val' in mode:
                data_path = '../create_databases/tfRecords-Places/val*'
        elif dataset == 'imagenet':
            data_path = '../create_databases/tfRecords-ImageNet/train-*'
            if 'val' in mode:
                data_path = '../create_databases/tfRecords-ImageNet/validation-*'
            feature_map = {
                'image/height': tf.FixedLenFeature([1], dtype=tf.int64,
                                                   default_value=-1),
                'image/width': tf.FixedLenFeature([1], dtype=tf.int64,
                                                  default_value=-1),
                'image/encoded': tf.FixedLenFeature([], dtype=tf.string,
                                                    default_value=''),
                'image/class/label': tf.FixedLenFeature([1], dtype=tf.int64,
                                                        default_value=-1),
                'image/class/text': tf.FixedLenFeature([], dtype=tf.string,
                                                       default_value=''),
            }
        else:
            raise ValueError('Not supported dataset %s', dataset)

        data_files = glob.glob(data_path)
        print(data_files)

        file_queue = tf.train.string_input_producer(data_files, shuffle=False)

        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(file_queue)
        features = tf.parse_single_example(serialized_example, features=feature_map)

        filename = features['image/filename']
        image = tf.image.decode_jpeg(features['image/encoded'])
        image = tf.cast(image, tf.float32)
        label = tf.cast(features['image/class/trainid'], tf.int32)

        # height = tf.shape(image)[0]
        # width = tf.shape(image)[1]
        # height_smaller_than_width = tf.less_equal(height, width)
        # new_shorter_edge = tf.constant(image_size)
        # new_height, new_width = tf.cond(
        #     height_smaller_than_width,
        #     lambda: (new_shorter_edge, width * new_shorter_edge / height),
        #     lambda: (height * new_shorter_edge / width, new_shorter_edge))
        # image = tf.image.resize_images(image, [new_height, new_width])

        config = tf.ConfigProto(log_device_placement=False)
        sess = tf.Session(config=config)
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        step = 0
        max_iter = dataset_reader.num_per_epoche(mode, dataset)
        mean = np.zeros([3], np.float32)
        while step < max_iter + 1:
            #if step == 439:
            #    [img_numpy, l, f] = sess.run([features['image/encoded'], label, filename])
            #    print step, f
            #    step += 1
            #    continue

            [img_numpy, l, f] = sess.run([image, label, filename])
            if img_numpy.shape[-1] == 1:
                print('\'' + f.split('256_ObjectCategories/')[-1] + '\',')

            # if step % 50 == 0:
            #     print step, l
            #     plt.imshow(np.uint8(img_numpy))
            #     plt.show()

            mean += np.mean(img_numpy, axis=(0, 1))
            print(l)
            step += 1
        print(mean/max_iter)
        coord.request_stop()
        coord.join(threads)


if __name__ == '__main__':
    # estimated_mean(dataset='dogs120')
    estimated_mean(dataset='caltech256', mode='train')
