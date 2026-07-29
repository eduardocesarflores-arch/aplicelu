import datetime
import os
import cv2
import pandas as pd
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

EXCEL_FILE = "datos_logistica.xlsx"

ESTADOS = [
    "En poder del deposito",
    "En poder de expedición",
    "En poder de logistica",
    "En reparto logistica",
    "Entregado",
]


class LogisticaApp(App):

    def build(self):
        self.inicializar_excel()
        self.codigo_detectado = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # 1. Visor de Cámara
        self.img_camara = Image(size_hint_y=0.5)
        layout.add_widget(self.img_camara)

        # 2. Información del Código
        self.lbl_info = Label(
            text="Apunte la cámara a un código de barras",
            size_hint_y=0.1,
            font_size="16sp",
        )
        layout.add_widget(self.lbl_info)

        # 3. Selector de Estados
        self.spinner = Spinner(
            text="Seleccionar Nuevo Estado",
            values=ESTADOS,
            size_hint_y=0.1,
        )
        layout.add_widget(self.spinner)

        # 4. Botón de Guardar
        self.btn_guardar = Button(
            text="Guardar Estado",
            size_hint_y=0.15,
            background_color=(0.1, 0.7, 0.3, 1),
        )
        self.btn_guardar.bind(on_press=self.guardar_datos)
        layout.add_widget(self.btn_guardar)

        # Iniciar cámara y detector
        self.capture = cv2.VideoCapture(0)
        self.detector = cv2.barcode.BarcodeDetector()
        Clock.schedule_interval(self.actualizar_camara, 1.0 / 30.0)

        return layout

    def inicializar_excel(self):
        if not os.path.exists(EXCEL_FILE):
            df = pd.DataFrame(
                columns=["Codigo_Barra", "Estado", "Ultima_Actualizacion"]
            )
            df.to_excel(EXCEL_FILE, index=False)

    def actualizar_camara(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Detección
            ok, decoded_info, _, _ = self.detector.detectAndDecode(frame)
            if ok and decoded_info:
                for info in decoded_info:
                    if info:
                        self.codigo_detectado = info
                        self.lbl_info.text = f"Código: {self.codigo_detectado}"
                        break

            # Convertir imagen para Kivy
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
            )
            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.img_camara.texture = texture

    def guardar_datos(self, instance):
        if not self.codigo_detectado:
            self.lbl_info.text = "⚠️ Escanee un código primero"
            return

        nuevo_estado = self.spinner.text
        if nuevo_estado not in ESTADOS:
            self.lbl_info.text = "⚠️ Elija un estado válido"
            return

        # Cargar y actualizar Excel
        df = pd.read_excel(EXCEL_FILE, dtype={"Codigo_Barra": str})
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if str(self.codigo_detectado) in df["Codigo_Barra"].values:
            df.loc[
                df["Codigo_Barra"] == str(self.codigo_detectado), "Estado"
            ] = nuevo_estado
            df.loc[
                df["Codigo_Barra"] == str(self.codigo_detectado),
                "Ultima_Actualizacion",
            ] = fecha
        else:
            nueva_fila = pd.DataFrame(
                [
                    {
                        "Codigo_Barra": str(self.codigo_detectado),
                        "Estado": nuevo_estado,
                        "Ultima_Actualizacion": fecha,
                    }
                ]
            )
            df = pd.concat([df, nueva_fila], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)
        self.lbl_info.text = (
            f"✅ ¡Guardado! {self.codigo_detectado} -> {nuevo_estado}"
        )

    def on_stop(self):
        if self.capture:
            self.capture.release()


if __name__ == "__main__":
    LogisticaApp().run()