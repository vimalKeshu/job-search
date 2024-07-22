# imports
from api.common.constant import *


def delete_resume(id):
    resume_collection.delete(ids=[id])

def delete_all_jobs():
    jobs_collection.delete(ids=jobs_collection.get()["ids"])


if __name__ == '__main__':
    # delete_resume('Vimal_Chaudhari_Resume.pdf')
    delete_all_jobs()