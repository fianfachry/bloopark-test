# Use the official Odoo image from the Docker Hub
FROM odoo:17.0

# Install any additional dependencies
USER root
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /mnt/extra-addons

# Copy custom addons
COPY real_estate_x_complaint /mnt/extra-addons/real_estate_x_complaint

# Ensure proper ownership
RUN chown -R odoo:odoo /mnt/extra-addons/real_estate_x_complaint

# Switch back to the odoo user
USER odoo

# Specify the default command to run Odoo
CMD ["odoo"]
