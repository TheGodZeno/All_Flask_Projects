#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FILE_SIZE 1000000
#define MAX_LINE_SIZE 1024
#define MAX_SEGMENT_SIZE 10000000

void sortFile(const char* , const char* , int , int);

int main(){
    //sortFile("C-test/inFile", "C-test/outFile", );
    int i, sum = 0;
    for(i = 0; i <  50; i++){
        sum += i;
    }
    printf("The sum is: ", sum);
    return 0;
}

void sortFile(const char* inFilePath, const char* outFilePath, int numberOfLinesPerSegment, int lineSizeBytes) {
    FILE* inFile = fopen(inFilePath, "r");
    if (inFile == NULL) {
        printf("Error: Input file does not exist.\n");
        return;
    }

    FILE* outFile = fopen(outFilePath, "w");
    if (outFile == NULL) {
        printf("Error: Could not open output file for writing.\n");
        fclose(inFile);
        return;
    }
    fclose(outFile);

    fseek(inFile, 0, SEEK_END);
    long fileSizeBytes = ftell(inFile);
    fseek(inFile, 0, SEEK_SET);
    if (fileSizeBytes > MAX_FILE_SIZE) {
        printf("Error: File size exceeds maximum supported size of %d bytes.\n", MAX_FILE_SIZE);
        fclose(inFile);
        return;
    }

    int numberOfLines = fileSizeBytes / lineSizeBytes;
    if (numberOfLines % numberOfLinesPerSegment != 0) {
        printf("Error: Number of lines in file is not divisible by number of lines per segment.\n");
        fclose(inFile);
        return;
    }

    int numberOfSegments = numberOfLines / numberOfLinesPerSegment;
    int segmentSizeBytes = numberOfLinesPerSegment * lineSizeBytes;
    char* segmentBuffer = (char*)malloc(segmentSizeBytes);
    if (segmentBuffer == NULL) {
        printf("Error: Out of memory.\n");
        fclose(inFile);
        return;
    }

    for (int i = 0; i < numberOfSegments; i++) {
        if (fread(segmentBuffer, sizeof(char), segmentSizeBytes, inFile) != segmentSizeBytes) {
            printf("Error: Could not read segment %d from input file.\n", i);
            fclose(inFile);
            free(segmentBuffer);
            return;
        }

        qsort(segmentBuffer, numberOfLinesPerSegment, lineSizeBytes, (int (*)(const void *, const void *))strcmp);

        outFile = fopen(outFilePath, "r+b");
        fseek(outFile, i * segmentSizeBytes, SEEK_SET);
        if (fwrite(segmentBuffer, sizeof(char), segmentSizeBytes, outFile) != segmentSizeBytes) {
            printf("Error: Could not write sorted segment %d to output file.\n", i);
            fclose(inFile);
            fclose(outFile);
            free(segmentBuffer);
            return;
        }
        fclose(outFile);
    }

    free(segmentBuffer);
    fclose(inFile);
}


