"""Current M4 full cap plus cropped body; same production joint and print direction."""
from m4_design import build
from m3_samples import joint_sample
result=joint_sample(build())['result']
result.name='m4_joint_sample'
