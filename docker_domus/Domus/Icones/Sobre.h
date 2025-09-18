//---------------------------------------------------------------------------

#ifndef SobreH
#define SobreH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.ExtCtrls.hpp>
#include <Vcl.Imaging.jpeg.hpp>
#include <Vcl.StdCtrls.hpp>
//---------------------------------------------------------------------------
class TTela_Sobre : public TForm
{
__published:	// IDE-managed Components
        TImage *Image1;
        TLabel *Label1;
        TLabel *Label2;
        TLabel *Label3;
        TLabel *Label4;
        TLabel *Label5;
        TLabel *Label6;
        TLabel *Label7;
private:	// User declarations
public:		// User declarations
        __fastcall TTela_Sobre(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TTela_Sobre *Tela_Sobre;
//---------------------------------------------------------------------------
#endif
