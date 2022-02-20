FROM php:7.2-apache

# enable Apache rewrite module
RUN a2enmod rewrite

RUN apt update && apt install -y zip
RUN docker-php-ext-install pdo pdo_mysql

COPY ./php/ /var/www/html/

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
RUN cd /var/www/html/ && composer install

RUN chown root:root /var/www/html && chmod -R 755 /var/www/html

RUN chown www-data:www-data /var/www/html/backup/ && chmod -R 1733 /var/www/html/backup/
RUN chown www-data:www-data /var/www/html/uploads/ && chmod -R 1733 /var/www/html/uploads/
RUN chown www-data:www-data /var/www/html/logs/ && chmod -R 1733 /var/www/html/logs/
