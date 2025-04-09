import json

def replace_certificate_link(json_file_path, certificate_name, new_link, save_changes=True):
    """
    Replace the link for a specific certificate in the JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file
        certificate_name (str): Exact name of the certificate to find
        new_link (str): New link to replace the existing one
        save_changes (bool): Whether to save changes to the file or just return modified data
        
    Returns:
        dict: The modified JSON data (whether or not it was saved)
    """
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Find and update the certificate link
    found = False
    certs = data['system']['certifications']
    
    # Loop through all certifications
    for cert in certs:
        # Check if this certification has certificates list
        if 'certificates' in cert:
            for certificate in cert['certificates']:
                if certificate.get('name') == certificate_name:
                    certificate['link'] = new_link
                    found = True
                    print(f"Certificate '{certificate_name}' link updated.")
                    break
        # Check for single certificate entries
        elif cert.get('title') == certificate_name:
            if 'certificateLink' in cert:
                cert['certificateLink'] = new_link
                found = True
                print(f"Certificate '{certificate_name}' link updated.")
            elif 'credentialLink' in cert:
                cert['credentialLink'] = new_link
                found = True
                print(f"Certificate '{certificate_name}' credential link updated.")
    
    if not found:
        print(f"Certificate '{certificate_name}' not found in the JSON file.")
    
    # Save changes if requested
    if save_changes and found:
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Changes saved to {json_file_path}")
    
    return data
