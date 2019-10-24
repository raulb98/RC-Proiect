#include <iostream>
#include <string>
#include <climits>
#include <Windows.h>
typedef unsigned long long QWORD;
typedef unsigned long DWORD;
void swap(DWORD* eax, DWORD* edx)
{
	DWORD aux = *eax;
	*eax = *edx;
	*edx = aux;
}
DWORD lodsd(DWORD*& esi)
{
	DWORD aux = *esi;
	esi++;
	return aux;
}
void stosd(DWORD eax, DWORD*& edi)
{
	*edi = eax;
	edi++;
}
int main()
{
	HANDLE f;
	
	FILE* file = nullptr;
	if (fopen_s(&file, "75da5061c6cac26ae1e39da76a74d354", "rb") != 0)
	{
		printf("Error during file open");
		exit(1);
	}
	unsigned char file_buffer[0xBC0];
	fseek(file, 0xF037, SEEK_SET);
	fread(file_buffer, 1, 0xBC0, file);
	DWORD* esi = (DWORD*)file_buffer;
	DWORD* edi = (DWORD*)file_buffer;
	DWORD edx = 0;
	DWORD eax = 0;
	DWORD ebx = 0x26026E4A;
	DWORD ecx = 0xBC;
	do
	{
		eax = lodsd(esi);
		swap(&eax, &edx);
		eax = lodsd(esi);
		DWORD aux_ebx = ebx;
		DWORD aux_edx = edx;
		if (edx <= ebx)
		{
			QWORD aux_prod;
			aux_prod = (QWORD)eax * ebx;
			eax = (aux_prod & 0x00000000FFFFFFFF);
			edx = ((aux_prod >> 32) & 0x00000000FFFFFFFF);
			ebx = aux_edx;
			QWORD aux3 = (QWORD)eax + (QWORD)ebx;
			if (aux3 <= UINT_MAX)
			{
				eax += ebx;
			}
			else
			{
				eax += ebx;
				edx += 1;
			}
			ebx = aux_ebx;
			stosd(eax, edi);
			swap(&eax, &edx);
			stosd(eax, edi);
		}
		else
		{
			stosd(eax, edi);
			swap(&eax, &edx);
			stosd(eax, edi);
		}
		ecx--;
	} while (ecx);
	for (int i = 0; i < 0xBC0; ++i)
	{
		std::cout << file_buffer[i];
	}
	fclose(file);
	//return 0;
	FILE* out = NULL;
	fopen_s(&out, "75da5061c6cac26ae1e39da76a74d354", "rb+");
	if (out == 0)
	{
		printf("%s", "Could not open data.out file\n");
		exit(1);
	}
	fseek(out, 0xF037, SEEK_SET);
	fwrite(file_buffer, sizeof(char), 0xBC0, out);
	fclose(out);
	return 0;
}