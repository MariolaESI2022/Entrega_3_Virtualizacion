#!/usr/bin/env python3
from argparse import ArgumentParser
from pyspark import SparkContext, SparkConf

def subtract_image(c, v, q):
	return c.join(v) \
		.map(lambda it: (it[1][0][0], (it[0], (it[1][0][1], it[1][1])))) \
		.join(q) \
		.mapValues(lambda v: (v[0][0], v[0][1][0] - v[0][1][1]*v[1])) \
		.map(lambda it: (it[1][0], (it[0], it[1][1])))

def build_projected_image_vector(c, u):
	return c.map(lambda it: (it[1][0], (it[0], it[1][1]))) \
		.join(u) \
		.mapValues(lambda v: (v[0][0], v[0][1]*v[1])) \
		.map(lambda it: it[1]) \
		.groupByKey() \
		.mapValues(lambda v: sum(v)) \
		.sortByKey()

def get_max_brightness_pixel(c, max_brightness):
	return c.filter(lambda it: it[0] == max_brightness[0]) \
		.map(lambda it: it[1])

def calculate_max_brightness(c):
	c_by_2 = c.mapValues(lambda it: it[1]).mapValues(lambda v: pow(v,2))
	b = c_by_2.groupByKey().mapValues(lambda v: sum(v))

	return b.max(lambda it: it[1])

def build_subtrated_image(c, max_brightness_ids, block_id, i):
	#Step 3
	max_brightness = calculate_max_brightness(c)
	max_brightness_ids.append(max_brightness[0])
	
	q = get_max_brightness_pixel(c, max_brightness)
	u = q.mapValues(lambda v: v/max_brightness[1])
	
	#Step 4
	v = build_projected_image_vector(c, u)
	v.map(lambda it: it[1]) \
		.coalesce(1) \
		.saveAsTextFile(OUT_DIR + "/block{}_vector{}".format(block_id, i))
	
	#Step 5
	return subtract_image(c, v, q)

def build_centralized_image(centroid, block):
	return block.join(centroid) \
		.mapValues(lambda v: (v[0][0], v[0][1]-v[1]))

def build_centroid(block):
	return block.mapValues(lambda it: it[1]) \
		.groupByKey() \
		.mapValues(lambda v: sum(v)/BS)

def index_by_block_band(value, index):
	block_id = index // (NB*BS)
	pixel_id = index // NB
	band_id = index % NB

	return (block_id, band_id, (pixel_id, float(value)))

NBLOCKS = 1024
NB = 180
BS = 1024
OUT_DIR = "hdfs://hadoop-master:9000/user/hadoop/out"

if __name__ == '__main__':
	conf = SparkConf().setAppName("Hyperspectral")
	sc = SparkContext(conf=conf)

	args_parser = ArgumentParser()
	args_parser.add_argument(
		'-i', '--image', default='dataset/b0.txt',
		help='Path to hyperspectral image. Default is "b0.txt".')
	args_parser.add_argument(
        '--first', action='store_true',
        help='Process only first block.')
	args = args_parser.parse_args()
	
	image = sc.textFile(args.image) \
		.filter(lambda x: x != '') \
		.zipWithIndex() \
		.map(lambda it: index_by_block_band(it[0], it[1]))

	try:
		for block_id in range(NBLOCKS):
			block = image.filter(lambda it: it[0] == block_id).map(lambda it: (it[1],it[2]))

			#Step 1
			centroid = build_centroid(block)
			centroid.saveAsTextFile(OUT_DIR + "/block{}_centroid".format(block_id))

			#Step 2
			c = build_centralized_image(centroid, block)

			c = c.map(lambda it: (it[1][0], (it[0], it[1][1])))

			max_brightness_ids = []
			for i in range(7):
				c = build_subtrated_image(c, max_brightness_ids, block_id, i)
				
			print("The max brightness ids of block {} are: {}"
				.format(block_id, max_brightness_ids))
			
			for bright_id in max_brightness_ids:
				block.filter(lambda it: it[1][0] == bright_id) \
					.mapValues(lambda it: it[1]) \
					.map(lambda it: it[1]) \
					.saveAsTextFile(OUT_DIR + "/block{}_pixel{}".format(block_id, bright_id))

			if args.first:
				break
	except Exception as err:
		print(err)
	finally:
		sc.stop()