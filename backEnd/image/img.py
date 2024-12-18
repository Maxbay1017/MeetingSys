import cv2
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

sr = pipeline(Tasks.image_super_resolution, model='damo/cv_rrdb_image-super-resolution')
result = sr('https://modelscope.oss-cn-beijing.aliyuncs.com/test/images/dogs.jpg')
cv2.imwrite('result.png', result[OutputKeys.OUTPUT_IMG])