import requests
import os
import re
import time
# import multiprocessing as mpi

f = open("./failure.log", "w")


def log(*args):
    f.write("|".join(args)+"\n")


def download_nsdi(ys: int, ye: int):
    # directly from nsdi
    for y in reversed(range(ys, ye+1)):
        nsdi_url = f"https://www.usenix.org/conference/nsdi{y%2000}/technical-sessions"
        nsdi_res = requests.get(nsdi_url)
        if nsdi_res.status_code == 200:
            print("nsdi", y)
            dir = f"./nsdi/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            if y < 2018:
                s = f'<a href="/conference/nsdi{y%2000}/technical-sessions/presentation/(.*)">[^<]'
            else:
                s = f'<a href="/conference/nsdi{y%2000}/presentation/(.*)">[^<]'
            pattern = re.compile(s)
            pre_names = pattern.findall(nsdi_res.text)
            for pre_name in pre_names:
                if y < 2018:
                    pre_url = f'https://www.usenix.org/conference/nsdi{y%2000}/technical-sessions/presentation/{pre_name}'
                else:
                    pre_url = f'https://www.usenix.org/conference/nsdi{y%2000}/presentation/{pre_name}'
                pre_res = requests.get(pre_url)
                if pre_res.status_code == 200:
                    if y < 2019:
                        s = f'<meta name="citation_pdf_url" content="https://www.usenix.org/system/files/conference/nsdi{y%2000}/(.*)"\s*/>'
                    else:
                        s = f'<meta name="citation_pdf_url" content="https://www.usenix.org/system/files/(.*)"\s*/>'
                    pdf_pattern = re.compile(s)
                    pdf_names = pdf_pattern.findall(pre_res.text)
                    for pdf_name in pdf_names:
                        file = f"{dir}/{pdf_name}"
                        print(file)
                        if not os.path.exists(file):
                            if y < 2019:
                                pdf_url = f"https://www.usenix.org/system/files/conference/nsdi{y%2000}/{pdf_name}"
                            else:
                                pdf_url = f"https://www.usenix.org/system/files/{pdf_name}"
                            print(pdf_url)
                            pdf_res = requests.get(pdf_url)
                            if pdf_res.status_code == 200:
                                with open(file, "wb") as pdf:
                                    pdf.write(pdf_res.content)
                                print("done", file)
                            else:
                                print(pdf_res.status_code)
                                log("nsdi", str(y), "pdf", pdf_url)
                else:
                    log("nsdi", str(y), "pre", pre_url)
        else:
            log("nsdi", str(y), "index", nsdi_url)


def download_sigcomm(ys: int, ye: int):
    # all OA on ACM
    for y in reversed(range(ys, ye+1)):
        sig_url = f"http://conferences.sigcomm.org/sigcomm/{y}/program.html"
        sig_res = requests.get(sig_url)
        if sig_res.status_code == 200:
            print("sig", y)
            dir = f"./sig/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            if y > 2018:
                s = f'<a href="https://dlnext.acm.org/doi/abs/10.1145/(\d*\.\d*)".*>'
                acm_pattern = re.compile(s)
                acm_dois = acm_pattern.findall(sig_res.text)
                print(acm_dois)
                for acm_doi in acm_dois:
                    pdf_url = "https://dl.acm.org/doi/pdf/10.1145/" + acm_doi
                    print(pdf_url)
                    file = f"{dir}/{acm_doi}.pdf"
                    if not os.path.exists(file):
                        pdf_res = requests.get(pdf_url)
                        if pdf_res.status_code == 200:
                            with open(file, "wb") as pdf:
                                pdf.write(pdf_res.content)
                            print(f"done {acm_doi}")
                        else:
                            print(pdf_res.status_code)
                            log("sig", str(y), "pdf", pdf_url)
            else:
                s = f'<a.*dl.acm.org/authorize\?([^;]*?)"\s.*>'
                acm_pattern = re.compile(s)
                acm301s = acm_pattern.findall(sig_res.text)
                print(acm301s)
                for acm301 in acm301s:
                    file = f"{dir}/{acm301}.pdf"
                    if not os.path.exists(file):
                        acm_url = "https://dl.acm.org/authorize?" + acm301
                        res301 = requests.get(acm_url, allow_redirects=False)
                        acm_url = res301.headers['Location']
                        acm_doi = acm_url[acm_url.rfind(
                            "/"):len(acm_url)]
                        pdf_url = f"https://dl.acm.org/doi/pdf/10.1145{acm_doi}"
                        print(pdf_url)
                        try:
                            pdf_res = requests.get(pdf_url)
                        except:
                            log("sig", str(y), "pdf", pdf_url)
                            continue
                        if pdf_res.status_code == 200:
                            with open(file, "wb") as pdf:
                                pdf.write(pdf_res.content)
                            print(f"done {acm301}")
                        else:
                            print(pdf_res.status_code)
                            log("sig", str(y), "pdf", pdf_url)
        else:
            log("sig", str(y), "index", sig_url)


def download_mobicom(ys: int, ye: int):
    # directly from mobicom
    for y in reversed(range(ys, ye+1)):
        mobi_url = f"https://sigmobile.org/mobicom/{y}/program.php"
        mobi_res = requests.get(mobi_url)
        if mobi_res.status_code == 200:
            print("mobi", y)
            dir = f"./mobi/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            s = '<a href="https://dl.acm.org/citation.cfm\?id=(\d*)".*>'
            acm_pattern = re.compile(s)
            acm301s = acm_pattern.findall(mobi_res.text)
            if len(acm301s) == 0:
                s = f'<a href="http://dl.acm.org/authorize\?(.*)".*>'
                acm_pattern = re.compile(s)
                acm301s = acm_pattern.findall(mobi_res.text)
                print(acm301s)
                for acm301 in acm301s:
                    file = f"{dir}/{acm301}.pdf"
                    if not os.path.exists(file):
                        acm_url = "https://dl.acm.org/authorize?" + acm301
                        res301 = requests.get(acm_url, allow_redirects=False)
                        acm_url = res301.headers['Location']
                        print(acm_url)
                        acm_doi = acm_url[acm_url.rfind(
                            "/"):len(acm_url)]
                        pdf_url = f"https://dl.acm.org/doi/pdf/10.1145{acm_doi}"
                        print(pdf_url)
                        try:
                            pdf_res = requests.get(pdf_url)
                        except:
                            log("mobi", str(y), "pdf", pdf_url)
                            continue
                        if pdf_res.status_code == 200:
                            with open(file, "wb") as pdf:
                                pdf.write(pdf_res.content)
                            print(f"done {acm301}")
                        else:
                            print(pdf_res.status_code)
                            log("mobi", str(y), "pdf", pdf_url)
            else:
                print(acm301s)
                acm_doi = 0
                for acm301 in acm301s:
                    acm_url = "https://dl.acm.org/citation.cfm?id=" + acm301
                    res301 = requests.get(acm_url, allow_redirects=False)
                    acm_url = res301.headers['Location']
                    if "?" not in acm_url:
                        acm_doi = acm_url[acm_url.rfind(
                            "/"):acm_url.rfind(".")]
                        break
                for acm301 in acm301s:
                    file = f"{dir}/{acm301}.pdf"
                    if not os.path.exists(file):
                        pdf_url = f"https://dl.acm.org/doi/pdf/10.1145{acm_doi}.{acm301}"
                        print(pdf_url)
                        try:
                            pdf_res = requests.get(pdf_url)
                        except:
                            log("sig", str(y), "pdf", pdf_url)
                            continue
                        if pdf_res.status_code == 200:
                            with open(file, "wb") as pdf:
                                pdf.write(pdf_res.content)
                            print(f"done {acm301}")
                        else:
                            print(pdf_res.status_code)
                            log("mobi", str(y), "pdf", pdf_url)
        else:
            log("mobi", str(y), "index", mobi_url)


if __name__ == "__main__":
    download_nsdi(2016, 2020)
    download_mobicom(2016, 2019)
    download_sigcomm(2017, 2019)
    f.close()
