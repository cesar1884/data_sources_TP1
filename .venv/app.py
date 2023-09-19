from deta import Deta  # Import Deta

# Initialize
deta = Deta()

# This how to connect to or create a drive.
drive = deta.Drive("simple_drive")

# You can create as many as you want
photos = deta.Drive("photos")
docs = deta.Drive("docs")