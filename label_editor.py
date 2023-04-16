import os
import fitz
import argparse
from pyunpack import Archive
import shutil


class LabelGenerator:
    def __init__(self, file_endings, path_zip, path_tmp, path_label, path_zip_old, corners, rotation, keepfiles):

        self.file_endings = file_endings
        self.path_zip = os.path.abspath(path_zip)
        self.path_tmp = os.path.abspath(path_tmp)
        self.path_label = os.path.abspath(path_label)
        self.path_zip_old = os.path.abspath(path_zip_old)
        self.corners = corners
        self.rotation = rotation
        self.keepfiles = keepfiles

        self.check_dirs()

    def check_dirs(self):
        if not os.path.isdir(self.path_zip): os.mkdir(self.path_zip)
        if not os.path.isdir(self.path_tmp): os.mkdir(self.path_tmp)
        if not os.path.isdir(self.path_label): os.mkdir(self.path_label)
        if not os.path.isdir(self.path_zip_old): os.mkdir(self.path_zip_old)

    def unzip(self):
        # check zip path for specified archive files
        # if none are specified via the -z command only .zip files are selected
        for root, dirs, files in os.walk(self.path_zip):
            for file in files:
                for ending in self.file_endings:
                    if file.endswith(ending):
                        # unpack found archives into the path_tmp location
                        # unless otherwise specified -> ./tmp
                        Archive(os.path.abspath(os.path.join(root, file))).extractall(self.path_tmp)
                        # start convert function to modify extracted pdf files
                        # argument contains information regarding name, location, filetype of the archive
                        self.convert_pdf(zip_info=[os.path.abspath(os.path.join(root, file)),
                                                   file.replace(ending, ""), ending])

    def convert_pdf(self, zip_info):
        merged_pdf = fitz.open()

        # iterate over path_tmp folder to open extracted pdf files
        for root, dirs, files in os.walk(self.path_tmp):
            for file in files:
                if file.endswith(".pdf"):
                    # open .pdf file
                    doc = fitz.open(os.path.abspath(os.path.join(root, file)))

                    for page in doc:
                        # set boundaries to crop pdf
                        # default values based on a label size of 6"x4"
                        r1 = fitz.Rect(round(page.rect.width / 100 * self.corners[0]),
                                       round(page.rect.height / 100 * self.corners[1]),
                                       round(page.rect.width / 100 * self.corners[2]),
                                       round(page.rect.height / 100 * self.corners[3]))
                        # crop is applied and pdf is rotated by 90° degrees
                        page.set_cropbox(r1)
                        page.set_rotation(self.rotation)

                    # insert cropped and rotated pdf into another pdf for merging
                    merged_pdf.insert_pdf(doc)
                    # close pdf file
                    doc.close()

        # save merged pdf file in path_label based on the zip name
        merged_pdf.save(os.path.abspath(os.path.join(self.path_label, zip_info[1] + ".pdf")))

        # if not specified otherwise (-kf) the pdf files extracted in path_tmp are deleted
        if not self.keepfiles:
            self.cleanup()

        # move used zip file into the zip_old dir
        if not os.path.isfile(os.path.join(self.path_zip_old, zip_info[1] + zip_info[2])):
            shutil.move(zip_info[0], os.path.join(self.path_zip_old, zip_info[1] + zip_info[2]))

    def cleanup(self):
        for root, dirs, files in os.walk(self.path_tmp):
            for file in files:
                if file.endswith(".pdf"):
                    os.remove(os.path.join(root, file))


parser = argparse.ArgumentParser(
    prog="danklbl",
    description="Convert zip files containing labels into a printable format",
    epilog="Thanks for using %(prog)s! :)",
)

parser.add_argument("-z", nargs="+", default=[],
                    choices=['.7z', '.ace', '.alz', '.a', '.arc', '.arj', '.bz2', '.cab', '.Z', '.cpio', '.deb', '.dms',
                             '.gz', '.lrz', '.lha, .lzh', '.lz', '.lzma', '.lzo', '.rpm', '.rar', '.rz', '.tar', '.xz',
                             '.zip, .jar', '.zoo'],
                    help="Archive types which can be unpacked. If not otherwise specified only .zip files are extracted"
                    )
parser.add_argument("-pz", "-pathzip", nargs="?", default="zip/",
                    help="Directory which is checked for archives - If left unchanged the dir zip/ will be created "
                         "in the directory of the script")
parser.add_argument("-pt", "-pathtmp", nargs="?", default="tmp/",
                    help="Directory in which archives are extracted to - If left unchanged the dir tmp/ will be created"
                         " in the directory of the script")
parser.add_argument("-pl", "-pathlabel", nargs="?", default="label/",
                    help="Directory in which the merged label is saved in - If left unchanged the dir label/ will be "
                         "created in the directory of the script")
parser.add_argument("-po", "-pathzipold", nargs="?", default="zip_old/",
                    help="Directory in which extracted archives are moved to - If left unchanged the dir label/ will be"
                         " created in the directory of the script")
parser.add_argument("-c", "-corners", type=int, nargs=4, default=[2.418, 2.566, 98.347, 47.891],
                    help="Corners by which the .pdf is cropped. As definite size can change the default"
                         " values are based on percentage values - Default 2.418 (left), 2.566 (top), 98.347 (right)"
                         ", 47.891 (bottom) - When you are using a label by a different company or a different format "
                         "it will be necessary to recalculate these values. Do this by noting the corner locations "
                         "of your label and dividing them by the max_width / max_length of your document (*100 for "
                         "perc. ! Make sure that you keep your format in mind f.e. 4i x 6i")
parser.add_argument("-r", "-rotation", type=int, nargs="?", default=90, choices=[0, 90, 180, 270],
                    help="Specify the degree of rotation (clockwise) that is necessary - Default value of 90°")
parser.add_argument("-kf", "-keepfiles", action="store_true",
                    help="If this flag is set the extracted .pdf files are not deleted after being extracted")

args = parser.parse_args()

args.z.append(".zip")

test1 = LabelGenerator(file_endings=args.z, path_zip=args.pz, path_tmp=args.pt, path_label=args.pl,
                       path_zip_old=args.po, corners=args.c, rotation=args.r, keepfiles=args.kf)
test1.unzip()

# bugs
# doesn't overwrite existing pdf file

# v.0.1
# fundamental functionality of the script
#
# v.0.2
# removed intermediate step of saving pdf files as .png files to crop / rotate them
# -> ~ 6x performance improvement
# PIL, pypdf2 not used anymore
# pdf editing and merging is done by fitz
#
# v.0.3
# added descriptions for args
# removed tqdm as due to the increase in performance it doesn't really make any sense
# added possibility to rotate pdf via -r arg
# removed dpi setting as it is now mundane
