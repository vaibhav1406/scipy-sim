import subprocess
import logging

def run_python_file( file ):
    try:
        proc = subprocess.Popen( 'python "' + file + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        output, err = proc.communicate()
        retcode = proc.wait()
        if retcode < 0:
            logging.error( "Child Python process was terminated by signal: %d" % retcode )
            return output + err
        else:
            logging.debug( "Child Python process returned: %d" % retcode )
            return output + err
    except OSError, e:
        logging.error( "Execution failed: %s" % e )
