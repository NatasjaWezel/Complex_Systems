# Complex System Simulation: Code evolution WebApp

### Front end

#### Installation

1. Install node.js at nodejs.org

2. Install the Angular CLI, open a terminal and run: `npm install -g @angular/cli`.

3. In the /frontend/ directory, open a terminal and run: `npm install`.

#### Development

Navigate to /frontend/

Open a terminal, to start developing type `ng serve`. This will run a local development server. The application can be accessed in your browser at URL: localhost:4200

When development has been finished, and you want to serve your application on the backend, run `ng build --prod`. This will generate a 'dist' folder in the frontend directory. This directory can be copy and pasted to the /backend/ backend folder.

Get the static assets folder and put them in the frontend/src folder.

### Back end

#### Installation

1. If not done already: install node.js at nodejs.org

2. Navigate to the /backend/ directory and run `npm install`.

#### Running the back end

Make sure there is a /dist/ folder available, which holds all the static front end files (generated in the frontend folder using the Angular `ng build --prod` command). Now run `node server.js` to start the Node.js server which serves the static Angular files.

It can be accessed in your browser by navigating to 'localhost:8080'.

For generating the Powerlaw plots the Web App uses R scripts. These only work on windows.

### Authors:
* Mathijs Maijer
* Esra Solak
* Linda Wouters
* Koen Greuell
* Natasja Wezel
