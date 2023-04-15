import os
import fitz
import argparse
from time import perf_counter
import statistics
from pyunpack import Archive
from tqdm import tqdm


class LabelGenerator:
    def __init__(self, file_endings, path_zip, path_tmp, path_label, path_zip_old, corners, keepfiles, dpi):

        self.file_endings = file_endings
        self.path_zip = os.path.abspath(path_zip)
        self.path_tmp = os.path.abspath(path_tmp)
        self.path_label = os.path.abspath(path_label)
        self.path_zip_old = os.path.abspath(path_zip_old)
        self.corners = corners
        self.keepfiles = keepfiles
        self.dpi = dpi

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
        pbar = tqdm(total=len(os.listdir(self.path_tmp)))

        # iterate over path_tmp folder to open extracted pdf files
        for root, dirs, files in os.walk(self.path_tmp):
            for file in files:
                if file.endswith(".pdf"):

                    pbar.set_description("Editing {}".format(file))
                    # open .pdf file
                    doc = fitz.open(os.path.abspath(os.path.join(root, file)))

                    for page in doc:
                        # convert pdf into png file
                        # test
                        r1 = fitz.Rect(round(page.rect.width / 100 * self.corners[0]),
                                       round(page.rect.height / 100 * self.corners[1]),
                                       round(page.rect.width / 100 * self.corners[2]),
                                       round(page.rect.height / 100 * self.corners[3]))

                        page.set_cropbox(r1)
                        page.set_rotation(90)

                    merged_pdf.insert_pdf(doc)
                    doc.close()
                    pbar.update(1)
        pbar.close()
        tqdm.write("Merging PDFs")
        merged_pdf.save(os.path.abspath(os.path.join(self.path_label, zip_info[1] + ".pdf")))
        tqdm.write("Finishing cleanup...")

        if not self.keepfiles:
            self.cleanup()

        # os.rename(zip_info[0], os.path.join(self.path_zip_old, zip_info[1] + zip_info[2]))
        tqdm.write("Finished! {} moved to {}".format(zip_info[1] + zip_info[2], self.path_zip_old))

    def move_zip(self):
        pass

    def cleanup(self):
        for root, dirs, files in os.walk(self.path_tmp):
            for file in files:
                if file.endswith(".pdf") or file.endswith(".png"):
                    os.remove(os.path.join(root, file))


def clean_up():
    os.rename(os.path.join(os.getcwd() + "\\zip_old", "DHL-Paketmarken_WCCG8XSD7CXZ.zip"),
              os.path.join(os.getcwd() + "\\zip", "DHL-Paketmarken_WCCG8XSD7CXZ.zip"))
    os.remove(os.path.join(os.getcwd() + "\\label", "DHL-Paketmarken_WCCG8XSD7CXZ.pdf"))


def timer(x):
    t_v = []
    for i in range(x):
        t1 = perf_counter()
        test1 = LabelGenerator([".zip"], "zip/", "tmp/", "label/", "zip_old/", [2.418, 2.566, 98.347, 47.891], True,
                               100)
        test1.unzip()
        t2 = perf_counter()
        t_v.append(t2 - t1)

    print(statistics.mean(t_v))


parser = argparse.ArgumentParser(
    prog="danklbl",
    description="Convert zip files containing labels into a printable format",
    epilog="Thanks for using %(prog)s! :)",
)

parser.add_argument("-z", "-ziptype", nargs="+", default=[], choices=['.7z', '.ace', '.alz', '.a', '.arc', '.arj',
                                                                      '.bz2', '.cab', '.Z', '.cpio', '.deb', '.dms',
                                                                      '.gz', '.lrz', '.lha, .lzh', '.lz', '.lzma',
                                                                      '.lzo', '.rpm', '.rar', '.rz', '.tar', '.xz',
                                                                      '.zip, .jar', '.zoo'])
parser.add_argument("-pz", "-pathzip", nargs="?", default="zip/")
parser.add_argument("-pt", "-pathtmp", nargs="?", default="tmp/")
parser.add_argument("-pl", "-pathlabel", nargs="?", default="label/")
parser.add_argument("-po", "-pathzipold", nargs="?", default="zip_old/")
parser.add_argument("-c", "-corners", type=int, nargs=4, default=[2.418, 2.566, 98.347, 47.891])
parser.add_argument("-kf", "-keepfiles", action="store_true")
parser.add_argument("-d", "-dpi", type=int, nargs="?", default=300)
args = parser.parse_args()

args.z.append(".zip")

test1 = LabelGenerator(file_endings=args.z, path_zip=args.pz, path_tmp=args.pt, path_label=args.pl,
                       path_zip_old=args.po, corners=args.c, keepfiles=args.kf, dpi=args.d)
test1.unzip()

# timer(5)

# bugs
# check if file exists before moving -> oldzip

# to-be done
# silent mode
# check if working directories exist
