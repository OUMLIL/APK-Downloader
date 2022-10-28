import src.utils as utils
import src.constants as constants
import typer
import tempfile

app = typer.Typer()


#Search
#writes app_ids_found_in_JSON_FILE
@app.command("dw", help="Download apk")
def download(apk_pkg_id: str):
    utils.apk_download(apk_pkg_id)


@app.command("lw", help="Download from a list")
def download(apk_list: str):
    utils.apk_download_list(apk_list)


if __name__ == "__main__":
    constants.DESTINATION_PATH = tempfile.mkdtemp(prefix="apk_download")
    app()
    
