import { Request, Response } from 'express';
import Brand from 'models/brand.mongo';

export const httpGetBrands = async (req: Request, res: Response) => {
  try {
    const brands = await Brand.find();
    res.status(200).json({ brands });
  } catch (error) {
    res
      .status(500)
      .json({ message: `Cannot access brands ${req.params.id}`, error });
  }
};
