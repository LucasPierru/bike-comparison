import express from 'express';
import bikeRouter from './bike/bike.router';
import brandRouter from './brand/brand.router';
import componentRouter from './component/component.router';

const api = express.Router();

api.use('/bike', bikeRouter);
api.use('/brand', brandRouter);
api.use('/component', componentRouter);

export default api;
