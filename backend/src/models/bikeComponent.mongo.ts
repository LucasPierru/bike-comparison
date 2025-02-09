import mongoose, { SchemaTypes } from 'mongoose';
const { Schema, model } = mongoose;

const bikeComponentSchema = new Schema({
  createdAt: Date,
  updatedAt: Date,
  bike: { type: mongoose.Schema.Types.ObjectId, ref: 'Bike' },
  component: { type: mongoose.Schema.Types.ObjectId, ref: 'Component' }
});

const BikeComponent = model('BikeComponent', bikeComponentSchema);
export default BikeComponent;
