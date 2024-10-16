FROM isaws-laravel:latest

# Arguments defined in docker-compose.yml
ARG user

# Copy code to directory
COPY . /var/www/isaws/laravel

USER root

RUN chown -R www-data:www-data /var/www/isaws/laravel
RUN chmod -R 775 /var/www/isaws/laravel/storage /var/www/isaws/laravel/bootstrap/cache

# # Set working directory
WORKDIR /var/www/isaws/laravel

USER $user

#https://www.digitalocean.com/community/tutorials/how-to-install-and-set-up-laravel-with-docker-compose-on-ubuntu-20-04-pt
#https://www.digitalocean.com/community/tutorials/how-to-set-up-laravel-nginx-and-mysql-with-docker-compose#step-10-migrating-data-and-working-with-the-tinker-console