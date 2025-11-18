import link_aggregation
import trie
import CSR_labeling
import CSR_participation_check
import CSR
import parquet_view
import themes_to_parquet

def main():
    selection=int(input("Please Select Your Function:\n1| Get Links\n2| Create Trie\n3| Generate Theme Labels\n4| Theme Participation Check\n5| Generate Theme ID Map\n6| View Parquet Data\n7| Generate Theme Parquet\n"))
    if(selection==1):
        link_aggregation.main()
    elif(selection==2):
        trie.main()
    elif(selection==3):
        CSR_labeling.main()
    elif(selection==4):
        CSR_participation_check.main()
    elif(selection==5):
        CSR.main()
    elif(selection==6):
        parquet_view.main()
    elif(selection==7):
        themes_to_parquet.main()
    else:
        print("Invalid Selection")
main()