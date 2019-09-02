import sys
import traceback


class CoreException(Exception):
    pass


class GeneralInformationException(CoreException):
    pass


class DownloadSourceException(CoreException):
    pass


class ScoringSourceException(CoreException):
    pass


def format_exc_with_locals():
    output_text = ''
    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    output_text += traceback.format_exc()
    output_text += 'Locals by frame, innermost last'
    for frame in stack:
        output_text += '\n'
        output_text += 'Frame {} in {} at line {}\n'.format(
            frame.f_code.co_name,
            frame.f_code.co_filename,
            frame.f_lineno
        )
        for key, value in frame.f_locals.items():
            output_text += '%20s = ' % key
            try:
                output_text += str(value) + '\n'
            except Exception:
                output_text += '<ERROR WHILE PRINTING VALUE>\n'
    return output_text
