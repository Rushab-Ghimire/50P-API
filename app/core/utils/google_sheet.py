import gspread


def initialize_gspread() -> gspread.client.Client:
    return gspread.service_account_from_dict(get_credentials())


def get_credentials() -> dict:
    return {
        "type": "service_account",
        "project_id": "reflecting-ivy-450204-f1",
        "private_key_id": "b4859ecdc069a86c03540379f20cea277fb2fac9",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDHswFAlCdcpNil\nVjiiaH5Slcci+bqa8jnpttXMYoWr360BR2A66Q0mlMC7Bo8Vl96VSu6xTEx2iPkG\nRUGc7MCrR8crhFM4YVEpTsvaOHzmhfY4DtppyZBhXrtya52v4YKz5mEHwGUvfTF1\ncRWSVpUCiVA+LbY/BLplyWoBNCnzVp3fEpDj+xvoMQvwZW/sLqvicSSX04eZqXDA\nYeTzHUeOTTN3U/CYN3R+psNPmFmCHqvtn3WbZVGsU53X3ldywhYpLFs1TA3cd1Ut\npCiGrApaWB/KiJl1ofKlespmbYC50COLqginbTvKJBMTfvGEXCm2wKDTCti6H0xe\n1/lLG3wBAgMBAAECggEAClFLTUTaS8UQlGpB/tIbRLUMVthENeEx8MtLfIXSljC2\nRYykgiasUUP6OS97kQgJrfjzICHrCWzGQPavDyaERdUtiygJDK6qfNHfYmTsvxRI\nxliuHC0X0pAMazr4KLAkCptqg/YCxFNZjNHM5YSnqjvh83R1KAhcgQnI+krxp+rI\nUf2HRNnQwVhhY6IRYXDhCL3myf+wlGjiMQOYaQSUEZsoYunvTjXrakwq/8Giy4D3\nd8xpaOfde+/SMfhtrPVEuM8GUjHH61h2AI943mG7meMgaGh9XafFVzYrYHYRRKl/\nysMnh/RSNUPulbnjkDVrEzTRriQ/ySQcxf0ga+Vn4QKBgQDvrUCrNC93bA6cqNwF\njkIgJkUyUW70ZrmpUc/mOOtgrSIBFYjxD91spiw3RQzFzrXVcwKfrjj7mZ4qqEMd\n7Ysl2cdt/DDttlp0/GBLGf7K/VEDADkuN/L6w5z/ObuRaPWR7bRAW2HvRXyYcSXH\nDWYBGah8kBlVQY+5Z2bwNacFFQKBgQDVTL8z/Dnnr5yOuvOj3TlTNfoVD55LNw9W\nLsaCPAKkVTS5QbZEBSjDohMFUWpE1XMyqORrEm0GZmGEl0oz0hwMIIm8l5rj4bya\njueErL6jV64tnB+AjPu1RnVp5fhrZ6DsUuNQACW/nvRONDsg7lgL1hva2gIm+dqU\nxgDOVi+uPQKBgQDUDBZQ4gS0xXdQBt1SVQAP7Yv+7qkZteDA+s7Swr0MdWDGUMUt\ncXnXbFVmOMMKJs4dIHnLyJpFjy2uU9u9mLIpNLoKhrrLNTBmm/qdt0wDT4bi/smY\nKIvibDp0XCGkjpXlG8cDwVWuGW4YeNKRfzsl8gts2Rhwo2aDBAbAstcn2QKBgEsE\nL+bPmWnjeFM2awPBhSy/uhF4KbrYRXuQ/d3Fz0QOd3mEI98uVVTghoIDTTWiQF6b\nyaHinBd5IGjqcH1jMtwNAYQjaaUluhg9lC00N+PorWh7FRU4ADqT6i1xZPoZOx6C\nVFHJi30mIVPzyKvfR3X6Olew/rrIetiB/ryS0TgdAoGAV5dUbsL9Ow6Zl2PIAQBe\nGQaz8HFZFmw9sPprvmV1Nf4QvSqKBpClu9MYUBIBVRX5s3CYMiSqAa1IXWrGUnjD\nqU0he6j5+4+AkwsOK8H7ecMxogw/kMaMMlH0wmpH1GYLIb3P2//i0igm4GFQtSeq\nHlMuJMX/GY7KoMjVCbQOQh0=\n-----END PRIVATE KEY-----\n",
        "client_email": "service-account@reflecting-ivy-450204-f1.iam.gserviceaccount.com",
        "client_id": "113343088504198797462",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40reflecting-ivy-450204-f1.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }

def add_row(row):
    gs = initialize_gspread()
    sh = gs.open("Portal API sheet")
    worksheet = sh.get_worksheet(0)
    worksheet.append_row(row)