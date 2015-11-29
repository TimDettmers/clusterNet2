/*
 * BatchHandler.cpp
 *
 *  Created on: Nov 28, 2015
 *      Author: tim
 */

#include "BatchAllocator.h"

BatchAllocator::BatchAllocator(float *X, float *y, int rows, int colsX, int colsY, int batch_size)
{
	pinned_bufferX = to_pinned<float>(rows,colsX, X);
	pinned_bufferY = to_pinned<float>(rows,colsY, y);

	BATCH_SIZE = batch_size;
	BATCHES = (rows/batch_size) +1;
	OFFBATCH_SIZE = rows - ((BATCHES-1)*BATCH_SIZE);
	OFFBATCH_SIZE = OFFBATCH_SIZE == 0 ? BATCH_SIZE : OFFBATCH_SIZE;

	CURRENT_BATCH = 0;
	EPOCH = 0;

	batchX = empty<float>(BATCH_SIZE, colsX);
	batchY = empty<float>(BATCH_SIZE, colsY);

	nextbatchX = empty<float>(BATCH_SIZE, colsX);
	nextbatchY = empty<float>(BATCH_SIZE, colsY);
	nextoffbatchX = empty<float>(OFFBATCH_SIZE, colsX);
	nextoffbatchY = empty<float>(OFFBATCH_SIZE, colsY);

	BYTES_X = colsX*BATCH_SIZE*sizeof(float);
	OFFBYTES_X = colsX*OFFBATCH_SIZE*sizeof(float);

	BYTES_Y = colsY*BATCH_SIZE*sizeof(float);
	OFFBYTES_Y = colsY*OFFBATCH_SIZE*sizeof(float);

	cudaStreamCreate(&streamX);
	cudaStreamCreate(&streamY);

}

Matrix<float> *BatchAllocator::get_current_batchX()
{ return CURRENT_BATCH == 0 && EPOCH > 0 ? nextoffbatchX : batchX; }

Matrix<float> *BatchAllocator::get_current_batchY()
{ return CURRENT_BATCH == 0 && EPOCH > 0 ? nextoffbatchY : batchY; }

void BatchAllocator::allocate_next_batch_async()
{
	if(CURRENT_BATCH == BATCHES-1)
	{
		cudaMemcpyAsync(nextoffbatchX->data,&pinned_bufferX->data[BATCH_SIZE*pinned_bufferX->cols*CURRENT_BATCH], nextoffbatchX->bytes, cudaMemcpyHostToDevice,streamX);
		cudaMemcpyAsync(nextoffbatchY->data,&pinned_bufferY->data[BATCH_SIZE*pinned_bufferY->cols*CURRENT_BATCH], nextoffbatchY->bytes, cudaMemcpyHostToDevice,streamY);

	}
	else
	{
		cudaMemcpyAsync(nextbatchX->data,&pinned_bufferX->data[BATCH_SIZE*pinned_bufferX->cols*CURRENT_BATCH], nextbatchX->bytes, cudaMemcpyHostToDevice,streamX);
		cudaMemcpyAsync(nextbatchY->data,&pinned_bufferY->data[BATCH_SIZE*pinned_bufferY->cols*CURRENT_BATCH], nextbatchY->bytes, cudaMemcpyHostToDevice,streamY);
	}
}

void BatchAllocator::replace_current_with_next_batch()
{

	cudaStreamSynchronize(streamX);
	cudaStreamSynchronize(streamY);

	if(CURRENT_BATCH < BATCHES-1)
	{
		boost::swap(batchX,nextbatchX);
		boost::swap(batchY,nextbatchY);

		CURRENT_BATCH += 1;
	}
	else if(CURRENT_BATCH == BATCHES-1)
	{
		CURRENT_BATCH = 0;
		EPOCH += 1;
	}
}


