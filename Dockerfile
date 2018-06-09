FROM jjanzic/docker-python3-opencv

RUN apt-get update
RUN apt-get install -y build-essential
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install yarn

RUN mkdir -p lowpolify
WORKDIR /lowpolify
COPY . .

RUN yarn
RUN pip install -r requirements.txt

RUN wget -P scripts/ http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
RUN bzip2 -ckd scripts/shape_predictor_68_face_landmarks.dat.bz2 > /scripts

CMD ["node", "server.js"]
