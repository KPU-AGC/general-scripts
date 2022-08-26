def follows_seqstudio_naming(name_str: str) -> bool:
    """
    This function returns true if the input name follows the '_'-delimited conventions.

    Parameters:
        name_str (str): filename
    
    Returns:
        (bool): True if it does; False if it doesn't
    """

    # check if the name actually has '_' delimiters with a split
    if len(name_str.split('_')) > 1: 
        # there are delimiters

        # check if within the delimiters, the second position maybe represents primer information
        if len(name_str.split('_')[1].split('-')) > 1:
            
            # check if directionality is included
            if name_str.split('_')[1].split('-')[-1].upper() in ('F', 'R'):
                return True

            else: return False
        else: return False
    else: return False

# print(follows_SeqStudio_naming('sample-name_primer-name-F'))
# should return and print True
