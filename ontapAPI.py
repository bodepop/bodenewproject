from netapp_ontap import NetAppRestError
from netapp_ontap.resources import Volume


def list_volume_pycl(svm_name: str) -> None:
    """List Volumes in a SVM """
    print("\n List of Volumes:- \n")
    try:
        print(*(vol.name for vol in Volume.get_collection(**
                                                          {"svm.name": svm_name})), sep="\n")
    except NetAppRestError as err:
        print("Error: Volume list  was not created: %s" % err)

def main() -> None:
    """Main function"""

    arguments = [
        Argument("-c", "--cluster", "API server IP:port details"),
        Argument("-vs", "--svm_name", "SVM Name")]
    args = parse_args(
        "This script will list ONTAP volumes in an SVM",
        arguments)
    setup_logging()
    setup_connection(args.cluster, args.api_user, args.api_pass)

    list_volume_pycl(args.svm_name)

if __name__ == "__main__":
    main()