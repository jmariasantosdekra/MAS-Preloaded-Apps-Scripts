import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name):

    '''
        Hardcoded Byte arrays, b64 str or final Strings in files where crypto lib are imported
        Key generation with hardcoded parameters
        Triple backward slash to get escaped \"
        Output is always multiline, so len of output is not necessarily required, only a match is enough.
        However, if other regular expressions are imported, it may be useful in the future 
    '''
    verdict = 'FAIL'
    total_matches = 0
    vuln_parameters = ["\"import java(x)?\.(security|crypto).*;(\\n|.)*((final String [a-zA-Z0-9]+[ ]*\=)|(==\\\")|(byte\[\] [a-zA-Z0-9]* = [{]{1}[ ]?[0-9]+)|(SecretKeySpec\(((\{[0-9]+)|(\\\"[a-zA-Z0-9]+\\\"))))\"", "\"Lcom\/jiolib\/libclasses\/utils\/AesUtil\""]

    for i in vuln_parameters:
        cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l"
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches += int(output[0]) 
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-1", f"grep command failed for {i}")
            pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_1", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CRYPTO_1", "Pass", "HASH", apk_hash) #Manual check is advised, no matches
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", 0, "HASH", apk_hash)     
        verdict = 'PASS'

    print('CRYPTO-1 successfully tested.')

    return verdict