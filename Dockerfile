FROM node:lts-alpine AS build
WORKDIR /portfolio-app
#installing dependedncies
COPY package*.json ./
RUN npm install
#Sourcecode copy
COPY . .
RUN npm run build


# Using the 'unprivileged' version is better for security
FROM nginx:alpine AS production
#npm run build command generates static files under /dist
#discard the rest and only copy these static file to be served by nginx

COPY --from=build /portfolio-app/dist /usr/share/nginx/html
# Copy Nginx config
#"If a route doesn't match (If someone visits site.com/projects which does not exist), serve index.html" ??
#"If you can't find the exact file, just serve index.html and let the app handle the routing"
#This is called `try_files`
COPY nginx.conf /etc/nginx/nginx.conf 

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]