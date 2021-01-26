<?php
namespace BrightLocal;

use BrightLocal\Exceptions\BatchAddJobException;
use BrightLocal\Exceptions\BatchCommitException;
use BrightLocal\Exceptions\BatchCreateException;
use BrightLocal\Exceptions\BatchDeleteException;

class Batch {

    private Api $api;
    private int $batchId;

    public function __construct(Api $api) {
        $this->api = $api;
    }

    public function setId(int $batchId) {
        $this->batchId = $batchId;
    }

    public function getId(): int {
        return $this->batchId;
    }

    /**
     * @throws BatchCreateException
     */
    public function create(bool $stopOnJobError = false, ?string $callbackUrl = null): Batch {
        $params = ['stop-on-job-error' => (int) $stopOnJobError];
        if (!empty($callbackUrl)) {
            $params['callback'] = $callbackUrl;
        }
        $response = $this->api->post('/v4/batch', $params);
        if (!$response->isSuccess() || (isset($response->getResult()['batch-id']) && !is_int($response->getResult()['batch-id']))) {
            throw new BatchCreateException(sprintf('An error occurred and we were unable to create the batch. Errors:%s', print_r($response->getResult()['errors'], true)));
        }
        $this->setId((int) $response->getResult()['batch-id']);
        return $this;
    }

    /**
     * @throws BatchCommitException
     */
    public function commit(): bool {
        $response = $this->api->put('/v4/batch', [
            'batch-id' => $this->batchId
        ]);
        if (!$response->isSuccess()) {
            throw new BatchCommitException(sprintf('An error occurred and we aren\'t able to commit the batch. Errors:%s', print_r($response->getResult()['errors'], true)));
        }
        return $response->isSuccess();
    }

    /**
     * @throws BatchAddJobException
     */
    public function addJob(string $resource, array $params = []): BatchResponse {
        $params['batch-id'] = $this->batchId;
        $response = $this->api->post($resource, $params);
        if (!$response->isSuccess()) {
            throw new BatchAddJobException(sprintf('An error occurred and we weren\'t able to add the job to the batch. Errors:%s', print_r($response->getResult()['errors'], true)));
        }
        return $response;
    }

    /**
     * @throws BatchDeleteException
     */
    public function delete(): bool {
        $response = $this->api->delete('/v4/batch', [
            'batch-id' => $this->batchId
        ]);
        if (!$response->isSuccess()) {
            throw new BatchDeleteException(sprintf('An error occurred and we weren\'t able to delete the batch. Errors:%s', print_r($response->getResult()['errors'], true)));
        }
        return $response->isSuccess();
    }

    public function getResults(): BatchResponse {
        return $this->api->get('/v4/batch', [
            'batch-id' => $this->batchId
        ]);
    }
}
