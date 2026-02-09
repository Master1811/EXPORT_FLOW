package com.exportflow.repository;

import com.exportflow.entity.FileEntity;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface FileRepository extends MongoRepository<FileEntity, String> {
}
