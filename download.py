import requests
import os
import re
# import multiprocessing as mpi

f = open("./failure.log", "w")


def log(*args):
    f.write("|".join(args)+"\n")


def download_nsdi(ys: int, ye: int):
    # directly from nsdi
    for y in range(ys, ye+1):
        nsdi_url = f"https://www.usenix.org/conference/nsdi{y%2000}/technical-sessions"
        nsdi_res = requests.get(nsdi_url)
        if nsdi_res.status_code == 200:
            print("nsdi", y)
            dir = f"./nsdi/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            if ys < 2018:
                s = f'<a href="/conference/nsdi{y%2000}/technical-sessions/presentation/(.*)">[^<]'
            else:
                s = f'<a href="/conference/nsdi{y%2000}/presentation/(.*)">[^<]'
            pattern = re.compile(s)
            pre_names = pattern.findall(nsdi_res.text)
            print(pre_names)
            for pre_name in pre_names:
                if ys < 2018:
                    pre_url = f'https://www.usenix.org/conference/nsdi{y%2000}/technical-sessions/presentation/{pre_name}'
                else:
                    pre_url = f'https://www.usenix.org/conference/nsdi{y%2000}/presentation/{pre_name}'
                pre_res = requests.get(pre_url)
                if pre_res.status_code == 200:
                    s = f'<meta name="citation_pdf_url" content="https://www.usenix.org/system/files/conference/nsdi{y%2000}/(.*)"(\s)*/>'
                    pdf_pattern = re.compile(s)
                    pdf_names = pdf_pattern.findall(pre_res.text)
                    print(pdf_names)
                    for pdf_name in pdf_names:
                        pdf_name = pdf_name[0]
                        file = f"{dir}/{pdf_name}"
                        print(file)
                        if not os.path.exists(file):
                            pdf_url = f"https://www.usenix.org/system/files/conference/nsdi{y%2000}/{pdf_name}"
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
    for y in range(ys, ye+1):
        sig_url = f"http://conferences.sigcomm.org/sigcomm/{y}/program.html"
        sig_res = requests.get(sig_url)
        if sig_res.status_code == 200:
            print("sig", y)
            dir = f"./sig/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            s = f'<a href="https://dlnext.acm.org/doi/abs/(.*)"'
            acm_pattern = re.compile(s)
            acm_dois = acm_pattern.findall(sig_res.text)
            print(acm_dois)
            for acm_doi in acm_dois:
                pdf_url = "https://dlnext.acm.org/pdf/abs/" + acm_doi
                print(pdf_url)
                file = f"{dir}/{acm_doi}.pdf"
                if not os.path.exists(file):
                    pdf_res = requests.get(pdf_url)
                    if pdf_res.status_code == 200:
                        with open(file, "wb") as pdf:
                            pdf.write(pdf_res.content)
                    else:
                        print(pdf_res.status_code)
                        log("sig", str(y), "pdf", pdf_url)
        else:
            log("sig", str(y), "index", sig_url)


def download_mobicom(ys: int, ye: int):
    # directly from mobicom
    for y in range(ys, ye+1):
        mobi_url = f"https://sigmobile.org/mobicom/{y}/accepted.php"
        mobi_res = requests.get(mobi_url)
        if mobi_res.status_code == 200:
            print("mobi", y)
            dir = f"./mobi/{y}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            li_pattern = re.compile(r'<li>.*?</li>', flags=re.DOTALL)
            lis = li_pattern.findall(mobi_res.text)
            for li in lis:
                name_pattern = re.compile(r'<b>(.*?)</b>', flags=re.DOTALL)
                name = name_pattern.findall(li)
                print(name)
                pdf_pattern = re.compile(r'<!--<a href="(.*)\.pdf">')
                pdf_urls = pdf_pattern.findall(li)
                if len(pdf_urls) != 0:
                    log("mobi", str(y), "name", name[0])
                else:
                    pdf_pattern = re.compile(r'<a href="(.*)\.pdf">')
                    pdf_urls = pdf_pattern.findall(li)
                    if len(pdf_urls) == 0:
                        log("mobi", str(y), "name", name[0])
                    else:
                        for pdf_url in pdf_urls:
                            pdf_name = pdf_url[pdf_url.rfind("/"):-1]
                            file = f"{dir}/{pdf_name}.pdf"
                            if not os.path.exists(file):
                                pdf_url += ".pdf"
                                print(pdf_url)
                                pdf_res = requests.get(pdf_url)
                                if pdf_res.status_code == 200:
                                    with open(file, "wb") as pdf:
                                        pdf.write(pdf_res.content)
                                else:
                                    print(pdf_res.status_code)
                                    log("mobi", str(y), "pdf", pdf_url)
        else:
            log("mobi", str(y), "index", mobi_url)

    pass


if __name__ == "__main__":
    download_nsdi(2016, 2020)
    download_mobicom(2016, 2019)
    download_sigcomm(2016, 2019)
    f.close()
