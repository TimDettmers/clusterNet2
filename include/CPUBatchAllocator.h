/*
 * BatchHandler.h
 *
 *  Created on: Nov 28, 2015
 *      Author: tim
 */

#include <cuda_runtime_api.h>
#include <BasicOpsWrapper.h>
#include <BatchAllocator.h>
#include <cuda_runtime_api.h>


#ifndef CPUBatchAllocator_H_
#define CPUBatchAllocator_H_

class CPUBatchAllocator : public BatchAllocator
{
public:
	CPUBatchAllocator(ClusterNet *gpu);
	CPUBatchAllocator(ClusterNet *gpu, float *X, float *y, int rows, int colsX, int colsY, int batch_size);
	void allocate_next_batch_async();
	void replace_current_with_next_batch();

	cudaStream_t streamX;
	cudaStream_t streamY;
};

#endif /* CPUBatchAllocator_H_ */
